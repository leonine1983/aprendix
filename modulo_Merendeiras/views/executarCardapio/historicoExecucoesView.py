from django.views.generic import ListView
from django.db.models import Count, Q
from django.contrib import messages
from modulo_Merendeiras.models import ExecucaoCardapioDia
from django.views.generic import ListView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from ..baseMerendeiraView import BaseMerendeiraView
from django.db.models import Q
from django.utils import timezone
from datetime import date

class HistoricoExecucoesView(BaseMerendeiraView, ListView):
    model = ExecucaoCardapioDia
    template_name = "modulo_merendeiras/cadapioHoje/historico_execucoes.html"
    context_object_name = 'execucoes'
    paginate_by = 5

    def get_queryset(self):
        escola = self.get_escola_usuario()
        qs = (
            ExecucaoCardapioDia.objects
            .filter(escola=escola)
            .select_related('cardapio_dia', 'executado_por')
            .prefetch_related('itens_executados')
            .order_by('-data')
        )

        # ── Filtros ──────────────────────────────────────
        q = self.request.GET.get('q', '').strip()
        status = self.request.GET.get('status', '')
        turno = self.request.GET.get('turno', '')
        data_de = self.request.GET.get('data_de', '')
        data_ate = self.request.GET.get('data_ate', '')

        if q:
            qs = qs.filter(
                Q(executado_por__first_name__icontains=q) |
                Q(executado_por__last_name__icontains=q) |
                Q(executado_por__username__icontains=q)
            )
        if status:
            qs = qs.filter(status=status)
        if turno:
            qs = qs.filter(turno=turno)
        if data_de:
            try:
                qs = qs.filter(data__gte=date.fromisoformat(data_de))
            except ValueError:
                pass
        if data_ate:
            try:
                qs = qs.filter(data__lte=date.fromisoformat(data_ate))
            except ValueError:
                pass

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        escola = self.get_escola_usuario()
        ctx['nome_escola'] = escola.nome_escola
        ctx['hoje'] = timezone.now().date()

        # Preservar filtros ativos no contexto (para paginação + exibição)
        params = self.request.GET.copy()
        params.pop('page', None)
        ctx['query_string'] = params.urlencode()
        ctx['filtros'] = {
            'q':       self.request.GET.get('q', ''),
            'status':  self.request.GET.get('status', ''),
            'turno':   self.request.GET.get('turno', ''),
            'data_de': self.request.GET.get('data_de', ''),
            'data_ate':self.request.GET.get('data_ate', ''),
        }
        ctx['status_choices'] = ExecucaoCardapioDia._meta.get_field('status').choices
        ctx['turno_choices']  = ExecucaoCardapioDia.TURNO_CHOICES
        return ctx
