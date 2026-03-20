from django.views.generic import DetailView
from django.contrib import messages
from django.db.models import F
from django.contrib.auth.mixins import LoginRequiredMixin

from core.permissions import GroupRequiredMixin
from core.groups.merenda import MERENDEIRA_GROUPS
from ..baseMerendeiraView import BaseMerendeiraView

from merendaEscolar.models import MovimentacaoEstoque


class MovimentacaoEstoqueDetailView(
    LoginRequiredMixin,
    GroupRequiredMixin,
    DetailView
):
    model = MovimentacaoEstoque
    template_name = "modulo_merendeiras/movimentaEstoque/movimentacao_detail.html"
    context_object_name = "movimentacao"

    group_required = MERENDEIRA_GROUPS  # ajustar depois

    def get(self, request, *args, **kwargs):
        messages.info(request, "Detalhes da movimentação carregados.")
        return super().get(request, *args, **kwargs)