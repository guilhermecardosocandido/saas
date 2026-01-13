from django.urls import path
from . import views

urlpatterns = [
    path("schedule/", views.ScheduleView.as_view(), name="availability_schedule"),

    # API
    path("api/slots/", views.available_slots_api, name="availability_slots_api"),
]