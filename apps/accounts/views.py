from django.contrib.auth import login
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView as AuthLogoutView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import UserRegistrationForm

class LoginView(AuthLoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

class LogoutView(AuthLogoutView):
    next_page = reverse_lazy('login')

class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        return response

def profile(request):
    return render(request, 'accounts/profile.html')  # A simple profile page for logged-in users