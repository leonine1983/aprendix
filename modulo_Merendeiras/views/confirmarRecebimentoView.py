from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from merendaEscolar.models import Transferencia
from admin_acessos.models import Notificacao

from .views import BaseMerendeiraView  # ajuste se estiver no mesmo arquivo


class ConfirmarRecebimentoView(BaseMerendeiraView, View):

    def post(self, request, pk):
        transferencia = get_object_or_404(
            Transferencia,
            pk=pk,
            escola_destino=self.get_escola_usuario(),
            status="EM_CONFERENCIA"
        )

        try:
            transferencia.receber(request.user)

            # 🔔 NOTIFICAÇÃO INSTITUCIONAL
            Notificacao.objects.create(
                usuario=transferencia.criado_por,
                escola=transferencia.escola_destino,
                titulo="Transferência confirmada pela escola",
                mensagem=f"A transferência {transferencia.numero} foi conferida e recebida.",
                tipo="TRANSFERENCIA_RECEBIDA"
            )

            messages.success(
                request,
                f"Transferência {transferencia.numero} confirmada com sucesso."
            )

        except Exception as e:
            messages.error(request, str(e))

        return redirect("modulo_merendeiras:transferencias_recebidas")