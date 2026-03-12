from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from core.permissions import GroupRequiredMixin
from core.groups.nutricionista import NUTRICIONISTA_GROUPS
from merendaEscolar.models import DescarteEstoque


class DescarteDetalhesView(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    """
    Visualização detalhada de um descarte específico da merenda escolar.
    Permite auditoria e conferência dos registros.
    """

    group_required = NUTRICIONISTA_GROUPS
    model = DescarteEstoque
    template_name = "merendaEscolar/estoque/descarte_detalhes.html"
    context_object_name = "descarte"

    def get_object(self, queryset=None):
        obj = get_object_or_404(DescarteEstoque, pk=self.kwargs.get("pk"))
        if not obj:
            messages.error(self.request, "Descarte não encontrado.")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adicionar informações extras caso necessário
        context["registrado_por"] = self.object.registrado_por
        return context