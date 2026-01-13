from django.contrib.auth.models import AbstractUser
from django.db import models

class UserAccount(AbstractUser):
    phone = models.CharField('Telefone', max_length=20, blank=True)
    is_provider = models.BooleanField('É prestador de serviço', default=False)
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
    
    def __str__(self):
        return self.username

class Appointment(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.date} at {self.time}"