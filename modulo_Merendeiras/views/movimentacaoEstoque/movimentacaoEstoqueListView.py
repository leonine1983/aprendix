from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.db.models import F
from django.contrib.auth.mixins import LoginRequiredMixin

from core.permissions import GroupRequiredMixin
from core.groups.merenda import MERENDEIRA_GROUPS

from merendaEscolar.models import MovimentacaoEstoque


class MovimentacaoEstoqueListView(
    LoginRequiredMixin,
    GroupRequiredMixin,
    ListView
):
    model = MovimentacaoEstoque
    template_name = "modulo_merendeiras/movimentaEstoque/movimentacao_list.html"
    context_object_name = "movimentacoes"
    paginate_by = 20

    group_required = MERENDEIRA_GROUPS  # ajustar após sua resposta

    def get_queryset(self):
        """
        🔥 Uso de select_related + annotate para performance institucional
        Evita N+1 queries ao trazer produto e usuário.
        """
        return (
            MovimentacaoEstoque.objects
            .select_related("produto", "usuario", "escola")
            .order_by("-id")
        )

    def get(self, request, *args, **kwargs):
        messages.info(request, "Listagem de movimentações de estoque carregada.")
        return super().get(request, *args, **kwargs)