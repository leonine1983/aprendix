from django.views.generic import DetailView
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from core.permissions import GroupRequiredMixin
from core.groups.merenda import MERENDEIRA_GROUPS
from .baseMerendeiraView import BaseMerendeiraView
from merendaEscolar.models import Transferencia


class TransferenciaEscolaDetailView(
    BaseMerendeiraView,
    GroupRequiredMixin,
    DetailView
):
    model = Transferencia
    template_name = "modulo_merendeiras/transferencia/transferencia_detail.html"
    context_object_name = "transferencia"
    group_required = MERENDEIRA_GROUPS

    def get_object(self, queryset=None):
        obj = super().get_object()

        escola = self.get_escola_usuario()

        # 🔒 SEGURANÇA INSTITUCIONAL
        if obj.escola_destino != escola:
            raise PermissionDenied("Você não tem acesso a esta transferência.")

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        transferencia = self.object

        context["itens"] = transferencia.itens.select_related(
            "produto",
            "estoque_origem",
            "produto__unidade_medida"
        )

        # 🧠 UX: status amigável
        context["status_label"] = {
            "RASCUNHO": "Rascunho",
            "ENVIADO": "Enviado",
            "EM_CONFERENCIA": "Em Conferência",
            "RECEBIDO": "Recebido",
        }.get(transferencia.status, transferencia.status)

        return context