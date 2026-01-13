from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "time_slot", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at",)  # removido 'updated_at'