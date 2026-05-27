from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

from admin_acessos.models import MessageUser
from  core.views.baseNutricionista import BaseNutricionistaView


# =========================================================
# LISTAR MENSAGENS
# =========================================================

class ListarMensagensView(BaseNutricionistaView, View):

    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):

        print("\n========== DEBUG MENSAGENS ==========")
        print("USUÁRIO:", request.user)
        print("ID:", request.user.id)

        todas = (
            MessageUser.objects
            .filter(destinatario=request.user)
            .select_related("remetente", "destinatario")
            .order_by("-data_envio")
        )

        print("TOTAL NO BANCO:", todas.count())

        for m in todas[:10]:
            print({
                "id": m.id,
                "assunto": m.assunto,
                "aberta": m.aberta,
                "exclude_msg": m.exclude_msg,
                "destinatario": m.destinatario_id,
            })

        # -----------------------------------------
        # NÃO LIDAS
        # -----------------------------------------

        nao_lidas = (
            todas
            .filter(aberta=False)
            .exclude(exclude_msg=True)
        )[:30]

        # -----------------------------------------
        # LIDAS
        # -----------------------------------------

        lidas = (
            todas
            .filter(aberta=True)
            .exclude(exclude_msg=True)
        )[:20]

        print("NÃO LIDAS:", nao_lidas.count())
        print("LIDAS:", lidas.count())

        # -----------------------------------------
        # SERIALIZAÇÃO
        # -----------------------------------------

        def serializar(qs):

            dados = []

            for m in qs:

                dados.append({
                    "id": m.pk,
                    "assunto": m.assunto or "",
                    "mensagem": m.mensagem or "",
                    "aberta": m.aberta,

                    "remetente": (
                        m.remetente.get_full_name()
                        if m.remetente
                        else "Sistema"
                    ),

                    "data_envio": (
                        m.data_envio.strftime("%d/%m/%Y %H:%M")
                        if m.data_envio
                        else ""
                    ),
                })

            return dados

        response = {
            "ok": True,

            "nao_lidas": serializar(nao_lidas),
            "lidas": serializar(lidas),

            "total_nao_lidas": nao_lidas.count(),
            "total_lidas": lidas.count(),
        }

        print("RETORNO:", response)
        print("====================================\n")

        return JsonResponse(response)


# =========================================================
# MARCAR COMO LIDA
# =========================================================

@method_decorator(require_POST, name="dispatch")
class MarcarMensagemLidaView(BaseNutricionistaView, View):

    http_method_names = ["post"]

    def post(self, request, pk, *args, **kwargs):

        msg = get_object_or_404(
            MessageUser.objects.select_related("destinatario"),
            pk=pk,
            destinatario=request.user
        )

        msg.marcar_como_lida()

        return JsonResponse({
            "ok": True,
            "mensagem": "Mensagem marcada como lida."
        })


# =========================================================
# EXCLUIR MENSAGEM
# =========================================================

@method_decorator(require_POST, name="dispatch")
class ExcluirMensagemView(BaseNutricionistaView, View):

    http_method_names = ["post"]

    def post(self, request, pk, *args, **kwargs):

        msg = get_object_or_404(
            MessageUser.objects.select_related("destinatario"),
            pk=pk,
            destinatario=request.user
        )

        # SOFT DELETE
        msg.exclude_msg = True

        msg.save(update_fields=["exclude_msg"])

        print(f"MENSAGEM {msg.pk} MARCADA COMO EXCLUÍDA")

        return JsonResponse({
            "ok": True,
            "mensagem": "Mensagem excluída."
        })