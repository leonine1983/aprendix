# admin_acessos/signals.py
"""
Signals responsáveis por disparar notificações Web Push automaticamente
sempre que novos registros forem criados em:

    • MessageUser               → mensagem direta para o destinatário
    • AtualizacaoNotificacaoSistema → notificação de sistema para o user
    • NotificacaoProduto        → notificação de produto para o usuario

Os envios são feitos de forma assíncrona em uma thread separada para
não bloquear a requisição HTTP principal.
"""

import logging
import threading

from django.db.models.signals import post_save
from django.dispatch          import receiver

from .models import MessageUser, AtualizacaoNotificacaoSistema, NotificacaoProduto

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# 🔧 UTILITÁRIO — envio em background
# ══════════════════════════════════════════════════════════════════════════════

def _enviar_em_background(user, titulo: str, corpo: str, url: str = "/"):
    """
    Dispara `_enviar_push` em uma thread separada para não atrasar
    a resposta HTTP que gerou o sinal.
    """
    t = threading.Thread(
        target=_enviar_push,
        args=(user, titulo, corpo, url),
        daemon=True,
    )
    t.start()


def _enviar_push(user, titulo: str, corpo: str, url: str = "/"):
    """
    Envia Web Push para todos os dispositivos registrados do usuário.
    Remove automaticamente subscriptions expiradas (HTTP 404 / 410).
    """
    try:
        from django.conf import settings
        from pywebpush   import webpush, WebPushException
        import json

        from .models import PushSubscription

        subscriptions = PushSubscription.objects.filter(user=user)
        if not subscriptions.exists():
            return

        payload = json.dumps({
            "title": titulo,
            "body":  corpo,
            "url":   url,
            "icon":  getattr(settings, "PUSH_ICON_DEFAULT", "/static/img/icon-192.png"),
            "badge": getattr(settings, "PUSH_BADGE_DEFAULT", "/static/img/badge-72.png"),
        })

        vapid_private = getattr(settings, "VAPID_PRIVATE_KEY", "")
        vapid_claims  = getattr(settings, "VAPID_CLAIMS", {"sub": "mailto:admin@escola.gov.br"})

        if not vapid_private:
            logger.warning("VAPID_PRIVATE_KEY não configurado — push ignorado.")
            return

        for sub in subscriptions:
            try:
                webpush(
                    subscription_info={
                        "endpoint": sub.endpoint,
                        "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                    },
                    data=payload,
                    vapid_private_key=vapid_private,
                    vapid_claims=vapid_claims,
                )
                logger.debug("Push enviado para %s → %s", user.username, titulo)

            except WebPushException as exc:
                status = exc.response.status_code if exc.response else None
                if status in (404, 410):
                    # Subscription revogada ou expirada — remove do banco
                    logger.info(
                        "Subscription expirada removida (HTTP %s): %s",
                        status, sub.endpoint[:60],
                    )
                    sub.delete()
                else:
                    logger.error(
                        "Erro ao enviar push para %s (HTTP %s): %s",
                        user.username, status, exc,
                    )

    except Exception as exc:
        # Nunca deve derrubar a requisição principal
        logger.exception("Falha inesperada no envio de push: %s", exc)


# ══════════════════════════════════════════════════════════════════════════════
# 📨 SIGNAL — MessageUser
# ══════════════════════════════════════════════════════════════════════════════

@receiver(post_save, sender=MessageUser)
def push_nova_mensagem(sender, instance: MessageUser, created: bool, **kwargs):
    """
    Notifica o destinatário quando uma nova mensagem direta é criada.
    Não dispara em atualizações (ex.: marcar como lida).
    """
    if not created:
        return

    remetente = instance.remetente
    nome_remetente = (
        remetente.get_full_name() or remetente.username
        if remetente else "Sistema"
    )

    _enviar_em_background(
        user   = instance.destinatario,
        titulo = f"📨 Nova mensagem de {nome_remetente}",
        corpo  = instance.assunto,
        url    = "/merenda/mensagens/",
    )


# ══════════════════════════════════════════════════════════════════════════════
# 🔔 SIGNAL — AtualizacaoNotificacaoSistema
# ══════════════════════════════════════════════════════════════════════════════

# Mapeamento de ícones por tipo (opcional — pode personalizar no SW)
_ICONE_TIPO = {
    "info":       "ℹ️",
    "aviso":      "⚠️",
    "urgente":    "🚨",
    "atualizado": "🔄",
}

@receiver(post_save, sender=AtualizacaoNotificacaoSistema)
def push_notificacao_sistema(sender, instance: AtualizacaoNotificacaoSistema, created: bool, **kwargs):
    """
    Notifica o usuário quando uma nova notificação de sistema é criada.
    """
    if not created:
        return

    icone = _ICONE_TIPO.get(instance.tipo, "🔔")

    _enviar_em_background(
        user   = instance.user,
        titulo = f"{icone} {instance.titulo}",
        corpo  = _extrair_texto(instance.mensagem),
        url    = "/merenda/",
    )


# ══════════════════════════════════════════════════════════════════════════════
# 📦 SIGNAL — NotificacaoProduto
# ══════════════════════════════════════════════════════════════════════════════

_ICONE_PRODUTO = {
    "ESTOQUE_BAIXO":           "📉",
    "PRODUTO_VENCENDO":        "⏰",
    "TRANSFERENCIA_ENVIADA":   "📤",
    "TRANSFERENCIA_RECEBIDA":  "📥",
    "DIVERGENCIA_ABERTA":      "⚡",
}

@receiver(post_save, sender=NotificacaoProduto)
def push_notificacao_produto(sender, instance: NotificacaoProduto, created: bool, **kwargs):
    """
    Notifica o usuário vinculado quando uma nova notificação de produto é criada.
    Monta a URL de destino usando a escola relacionada, se disponível.
    """
    if not created:
        return

    icone = _ICONE_PRODUTO.get(instance.tipo, "📦")

    # URL contextual: leva direto ao estoque da escola, quando disponível
    if instance.escola_id:
        url = f"/merenda/escola/{instance.escola_id}/estoque/"
    else:
        url = "/merenda/central/"

    _enviar_em_background(
        user   = instance.usuario,
        titulo = f"{icone} {instance.titulo}",
        corpo  = instance.mensagem,
        url    = url,
    )


# ══════════════════════════════════════════════════════════════════════════════
# 🔧 HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _extrair_texto(html_ou_texto: str | None) -> str:
    """
    Remove tags HTML simples do campo RichTextField para usar no corpo do push.
    Retorna no máximo 120 caracteres.
    """
    if not html_ou_texto:
        return ""
    try:
        import re
        texto = re.sub(r"<[^>]+>", " ", html_ou_texto)
        texto = re.sub(r"\s+", " ", texto).strip()
        return texto[:120] + ("…" if len(texto) > 120 else "")
    except Exception:
        return str(html_ou_texto)[:120]