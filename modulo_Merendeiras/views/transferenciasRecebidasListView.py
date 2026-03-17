from django.views.generic import ListView
from django.contrib import messages

from merendaEscolar.models import Transferencia
from core.permissions import GroupRequiredMixin
from core.groups.merenda import MERENDEIRA_GROUPS
from .baseMerendeiraView import BaseMerendeiraView


class TransferenciasAbertasListView(BaseMerendeiraView, ListView):
    """
    Lista todas as transferências em aberto para a escola vinculada ao usuário.
    """
    model = Transferencia
    template_name = "modulo_merendeiras/transferencia/conferir_transferencia.html"
    context_object_name = "transferencias"
    group_required = MERENDEIRA_GROUPS

    def get_queryset(self):
        escola = self.get_escola_usuario()  # Método herdado de BaseMerendeiraView

        if not escola:
            messages.warning(self.request, "Usuário não está vinculado a nenhuma escola.")
            return Transferencia.objects.none()

        return (
            Transferencia.objects
            .filter(escola_destino=escola)
            .exclude(status__in=["RASCUNHO", "CONFERIDA"])
            .order_by("-criado_em")
        )