# core/views/notificacoes_views.py

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect
from admin_acessos.models import AtualizacaoNotificacaoSistema


@login_required
@require_POST
def marcar_lida(request, pk):
    notif = get_object_or_404(
        AtualizacaoNotificacaoSistema, pk=pk, user=request.user
    )
    notif.lida = True
    notif.save(update_fields=["lida", "atualizada_em"])
    return JsonResponse({"ok": True})


@login_required
@require_POST
def marcar_todas_lidas(request):
    AtualizacaoNotificacaoSistema.objects.filter(
        user=request.user, lida=False
    ).update(lida=True)
    return JsonResponse({"ok": True})


@login_required
@require_POST
def excluir_notificacao(request, pk):
    notif = get_object_or_404(
        AtualizacaoNotificacaoSistema, pk=pk, user=request.user
    )
    notif.delete()
    return JsonResponse({"ok": True})


@login_required
@require_POST
def excluir_todas_lidas(request):
    AtualizacaoNotificacaoSistema.objects.filter(
        user=request.user, lida=True
    ).delete()
    return JsonResponse({"ok": True})