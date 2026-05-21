from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

from admin_acessos.models import AtualizacaoNotificacaoSistema, NotificacaoProduto
from  core.views.baseMerendeira import BaseMerendeiraView 


# ─────────────────────────────────────────────
# 🔔 MARCAR NOTIFICAÇÃO COMO LIDA
# ─────────────────────────────────────────────

class MarcarNotificacaoSistemaLidaView(BaseMerendeiraView, View):
    """
    POST /merendeiras/notificacoes/sistema/<pk>/marcar-lida/
    Marca uma AtualizacaoNotificacaoSistema como lida para o usuário autenticado.
    Retorna JSON para uso via fetch/HTMX.
    """

    def post(self, request, pk, *args, **kwargs):
        notif = get_object_or_404(
            AtualizacaoNotificacaoSistema,
            pk=pk,
            user=request.user,
        )

        if not notif.lida:
            notif.lida = True
            notif.save(update_fields=["lida", "atualizada_em"])

        return JsonResponse({"ok": True, "pk": pk, "tipo": "sistema"})


class MarcarNotificacaoProdutoLidaView(BaseMerendeiraView, View):
    """
    POST /merendeiras/notificacoes/produto/<pk>/marcar-lida/
    Marca uma NotificacaoProduto como lida para o usuário autenticado.
    Retorna JSON para uso via fetch/HTMX.
    """

    def post(self, request, pk, *args, **kwargs):
        notif = get_object_or_404(
            NotificacaoProduto,
            pk=pk,
            usuario=request.user,
        )

        if not notif.lida:
            notif.lida = True
            notif.save(update_fields=["lida"])

        return JsonResponse({"ok": True, "pk": pk, "tipo": "produto"})


# ─────────────────────────────────────────────
# 🗑️ DELETAR NOTIFICAÇÃO
# ─────────────────────────────────────────────

class DeletarNotificacaoSistemaView(BaseMerendeiraView, View):
    """
    POST /merendeiras/notificacoes/sistema/<pk>/deletar/
    Deleta uma AtualizacaoNotificacaoSistema somente se já estiver lida.
    """

    def post(self, request, pk, *args, **kwargs):
        notif = get_object_or_404(
            AtualizacaoNotificacaoSistema,
            pk=pk,
            user=request.user,
        )

        if not notif.lida:
            return JsonResponse(
                {"ok": False, "erro": "Marque a notificação como lida antes de excluir."},
                status=400,
            )

        notif.delete()
        return JsonResponse({"ok": True, "pk": pk, "tipo": "sistema"})


class DeletarNotificacaoProdutoView(BaseMerendeiraView, View):
    """
    POST /merendeiras/notificacoes/produto/<pk>/deletar/
    Deleta uma NotificacaoProduto somente se já estiver lida.
    """

    def post(self, request, pk, *args, **kwargs):
        notif = get_object_or_404(
            NotificacaoProduto,
            pk=pk,
            usuario=request.user,
        )

        if not notif.lida:
            return JsonResponse(
                {"ok": False, "erro": "Marque a notificação como lida antes de excluir."},
                status=400,
            )

        notif.delete()
        return JsonResponse({"ok": True, "pk": pk, "tipo": "produto"})


# ─────────────────────────────────────────────
# 🧹 MARCAR TODAS COMO LIDAS (bulk)
# ─────────────────────────────────────────────

class MarcarTodasLidasView(BaseMerendeiraView, View):
    """
    POST /merendeiras/notificacoes/marcar-todas-lidas/
    Marca todas as notificações não lidas do usuário como lidas (sistema + produto).
    """

    def post(self, request, *args, **kwargs):
        qtd_sistema = AtualizacaoNotificacaoSistema.objects.filter(
            user=request.user, lida=False
        ).update(lida=True)

        qtd_produto = NotificacaoProduto.objects.filter(
            usuario=request.user, lida=False
        ).update(lida=True)

        return JsonResponse({
            "ok": True,
            "marcadas": qtd_sistema + qtd_produto,
        })