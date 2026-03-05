
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()

class HistoricoAcesso(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="acessos")

    ip = models.GenericIPAddressField()
    user_agent = models.TextField()
    dispositivo = models.CharField(max_length=200, blank=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    data_acesso = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.data_acesso}"