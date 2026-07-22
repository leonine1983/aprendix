from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import ConfiguraPessoal

User = get_user_model()


@receiver(post_save, sender=User)
def criar_configuracao_pessoal_padrao(sender, instance, created, **kwargs):
    """
    Cria automaticamente uma configuração pessoal padrão 
    sempre que um novo usuário é criado no sistema.
    """
    if created:
        # get_or_create garante que não haverá erro de duplicidade 
        # caso o signal seja disparado mais de uma vez
        ConfiguraPessoal.objects.get_or_create(usuario=instance)