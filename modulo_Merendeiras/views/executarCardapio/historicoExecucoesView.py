from django.views.generic import ListView
from django.db.models import Count, Q
from django.contrib import messages
from modulo_Merendeiras.models import ExecucaoCardapioDia
from django.views.generic import ListView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from ..baseMerendeiraView import BaseMerendeiraView

class HistoricoExecucoesView(BaseMerendeiraView, ListView):
    template_name = "modulo_merendeiras/cadapioHoje/historico_execucoes.html"
    model = ExecucaoCardapioDia
    context_object_name = "execucoes"
    paginate_by = 10

    def get_queryset(self):
        escola = self.get_escola_usuario()

        # 🔒 HARD GUARD (importante institucionalmente)
        if not escola:
            messages.error(self.request, "Usuário sem vínculo com escola.")
            return ExecucaoCardapioDia.objects.none()

        queryset = (
            ExecucaoCardapioDia.objects
            .filter(escola=escola)
            .exclude(status='EM_EXECUCAO')
            .select_related('cardapio_dia', 'executado_por')
            .prefetch_related('itens_executados')
            .annotate(
                total_itens=Count('itens_executados'),
                total_executados=Count(
                    'itens_executados',
                    filter=Q(itens_executados__status='EXECUTADO')
                ),
                total_falhas=Count(
                    'itens_executados',
                    filter=Q(itens_executados__status__in=['CANCELADO', 'FALTANDO_ESTOQUE'])
                )
            )
            .order_by('-data', '-criado_em')
        )

        if not queryset.exists():
            messages.info(self.request, "Nenhuma execução de cardápio encontrada.")

        return queryset