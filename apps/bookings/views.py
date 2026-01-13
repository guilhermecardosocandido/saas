from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView
from django.views import View
from django.urls import reverse_lazy

from apps.availability.models import TimeSlot
from .models import Booking
from .forms import BookingForm

class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/booking_list.html'
    context_object_name = 'bookings'
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-created_at')

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

            # Garantia dupla: flag + ausência de booking ativo
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

            # cancela mantendo histórico
            booking.status = "cancelled"
            booking.save(update_fields=["status"])

            # só libera o slot se não existir outro booking ativo nele
            has_other_active = Booking.objects.filter(
                time_slot=ts,
                status__in=["pending", "confirmed"],
            ).exists()

            if not has_other_active:
                ts.is_available = True
                ts.save(update_fields=["is_available"])

        messages.info(request, "Agendamento cancelado.")
        return redirect("booking_list")