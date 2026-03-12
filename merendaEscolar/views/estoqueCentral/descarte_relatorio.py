from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone

from core.permissions import GroupRequiredMixin
from core.groups.nutricionista import NUTRICIONISTA_GROUPS

from merendaEscolar.models import DescarteEstoque
from rh.models import Escola

class RelatorioDescarteListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    group_required = NUTRICIONISTA_GROUPS
    model = DescarteEstoque
    template_name = "merendaEscolar/estoque/descarte_list.html"
    context_object_name = "descartes"
    paginate_by = 20
    ordering = ["-criado_em"]

    def get_queryset(self):
        queryset = DescarteEstoque.objects.select_related(
            "produto",
            "registrado_por",
            "estoque",
        )

        busca = self.request.GET.get("q")
        produto = self.request.GET.get("produto")
        motivo = self.request.GET.get("motivo")
        usuario = self.request.GET.get("usuario")
        data_inicio = self.request.GET.get("data_inicio")
        data_fim = self.request.GET.get("data_fim")

        if busca:
            queryset = queryset.filter(
                Q(produto__nome__icontains=busca) |
                Q(motivo__icontains=busca) |
                Q(registrado_por__username__icontains=busca)
            )

        if produto:
            queryset = queryset.filter(produto_id=produto)

        if motivo:
            queryset = queryset.filter(motivo=motivo)

        if usuario:
            queryset = queryset.filter(registrado_por_id=usuario)

        if data_inicio:
            queryset = queryset.filter(criado_em__date__gte=data_inicio)

        if data_fim:
            queryset = queryset.filter(criado_em__date__lte=data_fim)

        if not queryset.exists():
            messages.info(self.request, "Nenhum descarte encontrado com os filtros aplicados.")

        return queryset