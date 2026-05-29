# admin_acessos/push_utils.py
from pywebpush import webpush, WebPushException
from django.conf import settings
import json, logging

logger = logging.getLogger(__name__)

def send_push_notification(subscription, title, body, url="/"):
    """Dispara um push para uma PushSubscription."""
    try:
        webpush(
            subscription_info={
                "endpoint": subscription.endpoint,
                "keys": {
                    "p256dh": subscription.p256dh,
                    "auth":   subscription.auth,
                },
            },
            data=json.dumps({"title": title, "body": body, "url": url}),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": f"mailto:{settings.VAPID_EMAIL}"},
        )
    except WebPushException as e:
        logger.warning("Push falhou para %s: %s", subscription.user, e)

def notify_user(user, title, body, url="/"):
    """Envia push para todas as assinaturas ativas de um usuário."""
    from admin_acessos.models import PushSubscription
    for sub in PushSubscription.objects.filter(user=user):
        send_push_notification(sub, title, body, url)