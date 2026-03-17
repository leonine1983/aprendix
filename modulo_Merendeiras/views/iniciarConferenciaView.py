from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from merendaEscolar.models import Transferencia

from .views import BaseMerendeiraView  # ajuste se estiver no mesmo arquivo


class IniciarConferenciaView(BaseMerendeiraView, View):

    def post(self, request, pk):
        transferencia = get_object_or_404(
            Transferencia,
            pk=pk,
            escola_destino=self.get_escola_usuario()
        )

        if transferencia.status != "ENVIADO":
            messages.warning(
                request,
                "Transferência não está disponível para conferência."
            )
            return redirect("modulo_merendeiras:transferencias_recebidas")

        transferencia.status = "EM_CONFERENCIA"
        transferencia.save()

        messages.info(
            request,
            f"Conferência iniciada para {transferencia.numero}."
        )

        return redirect(
            "modulo_merendeiras:conferir_transferencia",
            pk=pk
        )