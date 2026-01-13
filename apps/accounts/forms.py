from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserAccount

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='E-mail')
    phone = forms.CharField(max_length=20, required=False, label='Telefone')
    
    class Meta:
        model = UserAccount
        fields = ['username', 'email', 'phone', 'password1', 'password2']