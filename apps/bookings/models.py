from django.db import models
from django.conf import settings
from django.db.models import Q

from apps.availability.models import TimeSlot

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('confirmed', 'Confirmado'),
        ('cancelled', 'Cancelado'),
        ('completed', 'Concluído'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Cliente'
    )

    # ERA OneToOneField -> agora FK para permitir histórico
    time_slot = models.ForeignKey(
        TimeSlot,
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name='Horário'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # Só 1 booking ATIVO por TimeSlot
            models.UniqueConstraint(
                fields=["time_slot"],
                condition=Q(status__in=["pending", "confirmed"]),
                name="uniq_active_booking_per_timeslot",
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.time_slot} ({self.status})"