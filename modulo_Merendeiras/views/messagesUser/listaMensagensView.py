from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404

from admin_acessos.models import MessageUser
from core.views.baseMerendeira import BaseMerendeiraView


# =========================================================
# LISTA
# =========================================================

from django.views.generic import TemplateView

class ListaMensagensView(BaseMerendeiraView, TemplateView):

    template_name = "modulo_merendeiras/messagensUser/listarMensagens.html"

    def get_context_data(self, **kwargs):

        ctx = super().get_context_data(**kwargs)

        mensagens = (
            MessageUser.objects
            .filter(destinatario=self.request.user)
            .select_related("remetente")
            .order_by("-data_envio")
        )

        ctx["mensagens"] = mensagens

        return ctx


# =========================================================
# MARCAR TODAS COMO LIDAS
# =========================================================

class MarcarMensagensLidasView(BaseMerendeiraView, View):

    def post(self, request, *args, **kwargs):

        mensagens = MessageUser.objects.filter(
            destinatario=request.user,
            aberta=False
        )

        for msg in mensagens:
            msg.marcar_como_lida()

        return JsonResponse({
            "ok": True
        })


# =========================================================
# MARCAR INDIVIDUAL
# =========================================================

class MarcarMensagemView(BaseMerendeiraView, View):

    def post(self, request, pk):

        msg = get_object_or_404(
            MessageUser,
            pk=pk,
            destinatario=request.user
        )

        msg.marcar_como_lida()

        return JsonResponse({
            "ok": True
        })


# =========================================================
# EXCLUIR
# =========================================================

class ExcluirMensagemView(BaseMerendeiraView, View):

    def post(self, request, pk):

        msg = get_object_or_404(
            MessageUser,
            pk=pk,
            destinatario=request.user
        )

        msg.delete()

        return JsonResponse({
            "ok": True
        })