from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView
from django.views import View
from django.urls import reverse_lazy

from apps.availability.models import TimeSlot
from .models import Booking
from .forms import BookingForm

class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "bookings/booking_list.html"
    context_object_name = "bookings"
    paginate_by = 20

    def get_queryset(self):
        qs = Booking.objects.select_related("user", "time_slot__provider").filter(user=self.request.user)

        # filtro por status (query param)
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)

        return qs.order_by("-time_slot__date", "-time_slot__start_time")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_filter"] = self.request.GET.get("status", "")
        return ctx


class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = "bookings/booking_form.html"
    success_url = reverse_lazy("booking_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = "pending"

        with transaction.atomic():
            ts = TimeSlot.objects.select_for_update().get(pk=form.cleaned_data["time_slot"].pk)

            if not ts.is_available:
                form.add_error("time_slot", "Este horário não está mais disponível.")
                return self.form_invalid(form)

            if Booking.objects.filter(time_slot=ts, status__in=["pending", "confirmed"]).exists():
                form.add_error("time_slot", "Este horário acabou de ser reservado. Selecione outro.")
                return self.form_invalid(form)

            ts.is_available = False
            ts.save(update_fields=["is_available"])

            response = super().form_valid(form)
            booking = self.object

            def _send():
                if booking.user.email:
                    send_mail(
                        subject="Confirmação de agendamento",
                        message=f"Seu agendamento foi criado para {booking.time_slot.date} às {booking.time_slot.start_time}.",
                        from_email=None,
                        recipient_list=[booking.user.email],
                        fail_silently=True,
                    )

            transaction.on_commit(_send)
            return response


class BookingCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, user=request.user)

        with transaction.atomic():
            ts = TimeSlot.objects.select_for_update().get(pk=booking.time_slot_id)

            booking.status = "cancelled"
            booking.save(update_fields=["status"])

            has_other_active = Booking.objects.filter(
                time_slot=ts,
                status__in=["pending", "confirmed"],
            ).exists()

            if not has_other_active:
                ts.is_available = True
                ts.save(update_fields=["is_available"])

        messages.info(request, "Agendamento cancelado.")
        return redirect("booking_list")


class ProviderBookingsView(LoginRequiredMixin, ListView):
    """
    Lista agendamentos dos clientes para o prestador logado (staff).
    """
    model = Booking
    template_name = "bookings/provider_bookings.html"
    context_object_name = "bookings"
    paginate_by = 50

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "Acesso restrito a prestadores.")
            return redirect("booking_list")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = Booking.objects.select_related("user", "time_slot").filter(
            time_slot__provider=self.request.user
        )

        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)

        return qs.order_by("-time_slot__date", "-time_slot__start_time")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_filter"] = self.request.GET.get("status", "")
        return ctx