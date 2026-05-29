import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from admin_acessos.models import PushSubscription


@login_required
@require_POST
def push_subscribe(request):

    try:

        data = json.loads(request.body)

        endpoint = data["endpoint"]

        p256dh = data["keys"]["p256dh"]

        auth = data["keys"]["auth"]

    except Exception:

        return JsonResponse(
            {"erro": "Payload inválido"},
            status=400
        )


    PushSubscription.objects.update_or_create(

        endpoint=endpoint,

        defaults={
            "user": request.user,
            "p256dh": p256dh,
            "auth": auth,
        }
    )

    return JsonResponse({
        "status": "ok"
    })


@login_required
@require_POST
def push_unsubscribe(request):

    try:

        data = json.loads(request.body)

        endpoint = data["endpoint"]

    except Exception:

        return JsonResponse(
            {"erro": "Payload inválido"},
            status=400
        )


    PushSubscription.objects.filter(
        user=request.user,
        endpoint=endpoint
    ).delete()

    return JsonResponse({
        "status": "removido"
    })