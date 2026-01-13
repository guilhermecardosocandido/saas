from datetime import date as date_type, datetime, timedelta
import calendar

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.utils.dateparse import parse_date
from django.views import View

from .forms import GenerateRecurringSlotsForm, DayOffForm
from .models import TimeSlot, DayOff


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return bool(self.request.user and self.request.user.is_staff)

    def handle_no_permission(self):
        # Se estiver logado mas não for staff, volta pro home
        if self.request.user.is_authenticated:
            return redirect("booking_list")
        return super().handle_no_permission()


def _daterange(start: date_type, end: date_type):
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)


class ScheduleView(LoginRequiredMixin, StaffRequiredMixin, View):
    template_name = "availability/schedule.html"

    def get(self, request):
        ctx = self._context(request)
        return render(request, self.template_name, ctx)

    def post(self, request):
        action = request.POST.get("action")

        if action == "generate":
            return self._post_generate(request)

        if action == "block_day":
            return self._post_block_day(request)

        if action == "unblock_day":
            return self._post_unblock_day(request)

        messages.error(request, "Ação inválida.")
        return redirect("availability_schedule")

    def _context(self, request):
        slots = (
            TimeSlot.objects
            .filter(provider=request.user)
            .order_by("-date", "start_time")[:300]
        )
        dayoffs = DayOff.objects.filter(provider=request.user).order_by("-date")[:60]
        return {
            "gen_form": GenerateRecurringSlotsForm(),
            "dayoff_form": DayOffForm(),
            "slots": slots,
            "dayoffs": dayoffs,
        }

    def _post_generate(self, request):
        form = GenerateRecurringSlotsForm(request.POST)
        if not form.is_valid():
            ctx = self._context(request)
            ctx["gen_form"] = form
            return render(request, self.template_name, ctx)

        month, year = form.cleaned_data.get("month"), form.cleaned_data.get("year")
        start_date, end_date = form.cleaned_data.get("start_date"), form.cleaned_data.get("end_date")

        if month and year:
            last_day = calendar.monthrange(year, month)[1]
            start_date = date_type(year, month, 1)
            end_date = date_type(year, month, last_day)

        weekdays = {int(x) for x in form.cleaned_data["weekdays"]}

        windows = [
            (form.cleaned_data["start_time"], form.cleaned_data["end_time"]),
        ]
        if form.cleaned_data.get("start_time_2") and form.cleaned_data.get("end_time_2"):
            windows.append((form.cleaned_data["start_time_2"], form.cleaned_data["end_time_2"]))

        slot_minutes = form.cleaned_data["slot_minutes"]
        break_minutes = form.cleaned_data["break_minutes"]

        created = 0
        skipped_blocked_days = 0

        with transaction.atomic():
            blocked = set(
                DayOff.objects.filter(provider=request.user, date__range=(start_date, end_date))
                .values_list("date", flat=True)
            )

            for d in _daterange(start_date, end_date):
                if d.weekday() not in weekdays:
                    continue
                if d in blocked:
                    skipped_blocked_days += 1
                    continue

                for (st, et) in windows:
                    start_dt = datetime.combine(d, st)
                    end_dt = datetime.combine(d, et)
                    cursor = start_dt

                    while cursor + timedelta(minutes=slot_minutes) <= end_dt:
                        slot_end = cursor + timedelta(minutes=slot_minutes)

                        _, was_created = TimeSlot.objects.get_or_create(
                            provider=request.user,
                            date=d,
                            start_time=cursor.time(),
                            end_time=slot_end.time(),
                            defaults={"is_available": True},
                        )
                        if was_created:
                            created += 1

                        cursor = slot_end + timedelta(minutes=break_minutes)

        msg = f"{created} horários criados."
        if skipped_blocked_days:
            msg += f" ({skipped_blocked_days} dia(s) ignorado(s) por bloqueio.)"
        messages.success(request, msg)
        return redirect("availability_schedule")

    def _post_block_day(self, request):
        form = DayOffForm(request.POST)
        if not form.is_valid():
            ctx = self._context(request)
            ctx["dayoff_form"] = form
            return render(request, self.template_name, ctx)

        d = form.cleaned_data["date"]
        reason = form.cleaned_data.get("reason") or ""

        # se houver booking ativo nesse dia, não bloquear (evita inconsistência)
        from apps.bookings.models import Booking

        has_active = Booking.objects.filter(
            time_slot__provider=request.user,
            time_slot__date=d,
            status__in=["pending", "confirmed"],
        ).exists()

        if has_active:
            messages.error(request, "Não é possível bloquear: existem agendamentos ativos nesse dia.")
            return redirect("availability_schedule")

        with transaction.atomic():
            DayOff.objects.get_or_create(provider=request.user, date=d, defaults={"reason": reason})
            TimeSlot.objects.filter(provider=request.user, date=d).update(is_available=False)

        messages.info(request, "Dia bloqueado (agenda desativada para a data).")
        return redirect("availability_schedule")

    def _post_unblock_day(self, request):
        form = DayOffForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Data inválida.")
            return redirect("availability_schedule")

        d = form.cleaned_data["date"]

        from apps.bookings.models import Booking

        with transaction.atomic():
            DayOff.objects.filter(provider=request.user, date=d).delete()

            # reabilita apenas slots sem booking ativo
            active_slot_ids = Booking.objects.filter(
                time_slot__provider=request.user,
                time_slot__date=d,
                status__in=["pending", "confirmed"],
            ).values_list("time_slot_id", flat=True)

            TimeSlot.objects.filter(provider=request.user, date=d).exclude(id__in=active_slot_ids).update(is_available=True)

        messages.success(request, "Dia desbloqueado.")
        return redirect("availability_schedule")


@login_required
def available_slots_api(request):
    """
    GET /availability/api/slots/?date=YYYY-MM-DD[&provider=<id>]
    """
    date_str = request.GET.get("date")
    provider_id = request.GET.get("provider")

    d = parse_date(date_str) if date_str else None
    if not isinstance(d, date_type):
        return JsonResponse({"results": []})

    qs = TimeSlot.objects.filter(date=d, is_available=True).order_by("start_time").select_related("provider")

    if provider_id:
        qs = qs.filter(provider_id=provider_id)

    # não mostra horários de dias bloqueados (por provider)
    if provider_id:
        if DayOff.objects.filter(provider_id=provider_id, date=d).exists():
            return JsonResponse({"results": []})
    else:
        blocked_provider_ids = set(DayOff.objects.filter(date=d).values_list("provider_id", flat=True))
        if blocked_provider_ids:
            qs = qs.exclude(provider_id__in=blocked_provider_ids)

    data = [
        {
            "id": s.id,
            "start_time": s.start_time.strftime("%H:%M"),
            "end_time": s.end_time.strftime("%H:%M"),
            "provider_id": s.provider_id,
            "provider_name": getattr(s.provider, "username", str(s.provider)),
        }
        for s in qs
    ]
    return JsonResponse({"results": data})


@login_required
def calendar_view(request):
    """
    Página de calendário visual
    """
    return render(request, "availability/calendar.html")


@login_required
def calendar_events_api(request):
    """
    Retorna eventos no formato FullCalendar
    GET /availability/api/calendar-events/?start=YYYY-MM-DD&end=YYYY-MM-DD
    """
    from datetime import date as date_type
    from django.utils.dateparse import parse_date
    
    start_str = request.GET.get("start")
    end_str = request.GET.get("end")
    
    start = parse_date(start_str) if start_str else None
    end = parse_date(end_str) if end_str else None
    
    if not (isinstance(start, date_type) and isinstance(end, date_type)):
        return JsonResponse({"events": []})
    
    # busca slots disponíveis no intervalo
    slots = TimeSlot.objects.filter(
        date__gte=start,
        date__lte=end,
        is_available=True
    ).select_related("provider")
    
    # ignora dias bloqueados
    blocked_dates = set(
        DayOff.objects.filter(date__gte=start, date__lte=end)
        .values_list("date", "provider_id")
    )
    
    events = []
    for s in slots:
        if (s.date, s.provider_id) in blocked_dates:
            continue
        
        events.append({
            "id": s.id,
            "title": f"{s.start_time.strftime('%H:%M')} - {s.provider.username}",
            "start": f"{s.date}T{s.start_time}",
            "end": f"{s.date}T{s.end_time}",
            "url": f"/novo/?slot={s.id}",  # link para agendar
            "color": "#28a745",
        })
    
    return JsonResponse(events, safe=False)