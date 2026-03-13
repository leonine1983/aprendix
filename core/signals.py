from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import PerfilUsuario

from django.contrib.auth.signals import user_logged_in
from django.utils.timezone import now

from core.models.acesso import HistoricoAcesso

User = get_user_model()


@receiver(post_save, sender=User)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(user=instance)


@receiver(post_save, sender=User)
def salvar_perfil_usuario(sender, instance, **kwargs):
    if hasattr(instance, "perfilusuario"):
        instance.perfilusuario.save()



def get_client_ip(request):
    """Obtém o IP real do usuário considerando proxies."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_device(user_agent):
    """Classificação simples do dispositivo."""
    if not user_agent:
        return ""

    ua = user_agent.lower()

    if "mobile" in ua:
        return "Mobile"
    if "tablet" in ua:
        return "Tablet"
    if "windows" in ua or "linux" in ua or "mac" in ua:
        return "Desktop"

    return "Desconhecido"


@receiver(user_logged_in)
def registrar_acesso(sender, request, user, **kwargs):

    ip = get_client_ip(request)
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    dispositivo = get_device(user_agent)

    HistoricoAcesso.objects.create(
        user=user,
        ip=ip,
        user_agent=user_agent,
        dispositivo=dispositivo,
    )