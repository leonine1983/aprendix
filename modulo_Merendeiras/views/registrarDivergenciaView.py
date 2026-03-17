from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from merendaEscolar.models import Transferencia, DivergenciaEntrega

from .views import BaseMerendeiraView  # ajuste se estiver no mesmo arquivo


class RegistrarDivergenciaView(BaseMerendeiraView, View):

    def post(self, request, pk, item_id):
        transferencia = get_object_or_404(
            Transferencia,
            pk=pk,
            escola_destino=self.get_escola_usuario(),
            status="EM_CONFERENCIA"
        )

        item = get_object_or_404(
            transferencia.itens,
            pk=item_id
        )

        quantidade_recebida = request.POST.get("quantidade_recebida")
        descricao = request.POST.get("descricao")

        try:
            quantidade_recebida = float(quantidade_recebida)

            DivergenciaEntrega.objects.create(
                transferencia=transferencia,
                produto=item.produto,
                quantidade_enviada=item.quantidade,
                quantidade_recebida=quantidade_recebida,
                descricao=descricao,
                registrado_por=request.user
            )

            messages.warning(
                request,
                f"Divergência registrada para {item.produto.nome}."
            )

        except Exception as e:
            messages.error(
                request,
                f"Erro ao registrar divergência: {str(e)}"
            )

        return redirect(
            "modulo_merendeiras:conferir_transferencia",
            pk=pk
        )