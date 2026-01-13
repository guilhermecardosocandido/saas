from django.urls import path
from . import views

urlpatterns = [
    path("schedule/", views.ScheduleView.as_view(), name="availability_schedule"),

    # API
    path("api/slots/", views.available_slots_api, name="availability_slots_api"),
    path("calendario/", views.calendar_view, name="availability_calendar"),
    path("api/calendar-events/", views.calendar_events_api, name="availability_calendar_events"),
]