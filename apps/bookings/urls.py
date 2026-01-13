from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookingListView.as_view(), name='booking_list'),
    path('novo/', views.BookingCreateView.as_view(), name='booking_create'),
    path('<int:pk>/cancelar/', views.BookingCancelView.as_view(), name='booking_cancel'),
    path('prestador/agendamentos/', views.ProviderBookingsView.as_view(), name='provider_bookings'),
]