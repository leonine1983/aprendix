from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=20, blank=True)
    cargo = models.CharField(max_length=100, blank=True)
    ultimo_acesso_ip = models.GenericIPAddressField(null=True, blank=True)

    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Perfil - {self.user.username}"
    



@receiver(post_save, sender=User)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(user=instance)