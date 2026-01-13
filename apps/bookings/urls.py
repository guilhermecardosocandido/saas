from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookingListView.as_view(), name='booking_list'),
    path('booking/new/', views.BookingCreateView.as_view(), name='booking_create'),
    path('booking/<int:pk>/cancel/', views.BookingCancelView.as_view(), name='booking_cancel'),
]