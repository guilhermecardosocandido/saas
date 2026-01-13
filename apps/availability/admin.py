from django.contrib import admin
from .models import TimeSlot

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['date', 'start_time', 'end_time', 'provider', 'is_available']
    list_filter = ['is_available', 'date', 'provider']
    search_fields = ['provider__username']
    date_hierarchy = 'date'