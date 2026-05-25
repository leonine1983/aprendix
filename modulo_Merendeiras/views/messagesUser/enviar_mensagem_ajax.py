# views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from admin_acessos.models import MessageUser
from core.views.baseMerendeira import BaseMerendeiraView

@login_required
@require_POST
def enviar_mensagem_ajax(request):
    User = get_user_model()
    destinatario_id = request.POST.get("destinatario_id")
    assunto = request.POST.get("assunto", "").strip()
    mensagem = request.POST.get("mensagem", "").strip()

    if not destinatario_id or not assunto or not mensagem:
        return JsonResponse({"ok": False, "erro": "Campos obrigatórios faltando"})

    try:
        destinatario = User.objects.get(pk=destinatario_id)
    except User.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Destinatário não encontrado"})

    MessageUser.objects.create(
        remetente=request.user,
        destinatario=destinatario,
        assunto=assunto,
        mensagem=mensagem,
    )
    return JsonResponse({"ok": True})


# view para retornar usuários dos grupos permitidos
@login_required
def destinatarios_ajax(request):
    from django.contrib.auth.models import Group
    grupos = Group.objects.filter(name__in=["Nutricionista", "Merendeira"])
    users = get_user_model().objects.filter(groups__in=grupos).exclude(pk=request.user.pk)
    data = [{"id": u.pk, "nome": u.get_full_name() or u.username, "grupo": u.groups.first().name} for u in users]
    return JsonResponse({"destinatarios": data})



# VIEWS.PY

from django.http import JsonResponse
from django.views import View

from admin_acessos.models import MessageUser


class MarcarMensagensLidasView( BaseMerendeiraView, View):

    def post(self, request, *args, **kwargs):

        MessageUser.objects.filter(
            destinatario=request.user,
            aberta=False
        ).update(
            aberta=True
        )

        return JsonResponse({
            "ok": True
        })