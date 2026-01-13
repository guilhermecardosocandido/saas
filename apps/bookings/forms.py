from django import forms

from .models import Booking
from apps.availability.models import TimeSlot


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["time_slot"]
        widgets = {"time_slot": forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["time_slot"].queryset = TimeSlot.objects.filter(is_available=True)