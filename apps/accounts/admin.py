from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserAccount

@admin.register(UserAccount)
class UserAccountAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_provider', 'is_staff']
    list_filter = ['is_provider', 'is_staff', 'is_superuser']
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('phone', 'is_provider')}),
    )