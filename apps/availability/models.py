from django.db import models
from django.conf import settings

class TimeSlot(models.Model):
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Prestador')
    date = models.DateField('Data')
    start_time = models.TimeField('Horário Início')
    end_time = models.TimeField('Horário Fim')
    is_available = models.BooleanField('Disponível', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "date", "start_time", "end_time"],
                name="uniq_timeslot_provider_date_start_end",
            )
        ]

    def __str__(self):
        return f"{self.date} - {self.start_time} às {self.end_time}"


class DayOff(models.Model):
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Prestador")
    date = models.DateField("Data")
    reason = models.CharField("Motivo", max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "date"],
                name="uniq_dayoff_provider_date",
            )
        ]

    def __str__(self):
        return f"{self.date} ({self.provider})"