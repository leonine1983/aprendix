"""
modulo_merendeiras/views_execucao_avulsa.py

View para execução avulsa de receita — independente do cardápio do dia.
A merendeira escolhe qualquer receita cujos ingredientes estejam disponíveis
no estoque da escola.
"""

from django.views.generic import ListView
from django.db.models import Sum


from modulo_Merendeiras.models import (
    ExecucaoReceitaCozinha
)
from django.db.models import Q, Sum, Count
from django.views.generic import ListView
from core.views.baseMerendeira import BaseMerendeiraView



class ListaExecucoesView(BaseMerendeiraView, ListView):
    """
    Lista as execuções avulsas de receitas da escola vinculada
    à merendeira logada, com suporte a:
      - busca textual (receita, observação, usuário)
      - filtro por status
      - filtro por período (data_ini / data_fim)
      - ordenação
      - métricas agregadas no contexto
    """

    model = ExecucaoReceitaCozinha
    template_name = "modulo_merendeiras/cozinha/lista_merenda_avulsa.html"
    context_object_name = "execucoes_avulsas"
    paginate_by = 20

    # ─────────────────────────────────────────────
    # 🔍 QUERYSET BASE
    # ─────────────────────────────────────────────

    def get_base_queryset(self):
        """Queryset filtrado apenas pela escola — sem filtros da URL."""
        escola = self.escola_usuario
        if not escola:
            return ExecucaoReceitaCozinha.objects.none()

        return (
            ExecucaoReceitaCozinha.objects
            .filter(escola=escola)
            .select_related(
                "receita",
                "iniciado_por",
                "finalizado_por",
                "escola",
            )
        )

    def get_queryset(self):
        qs = self.get_base_queryset()
        params = self.request.GET

        # ── Busca textual ──────────────────────────
        q = params.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(receita__nome__icontains=q)
                | Q(observacoes__icontains=q)
                | Q(iniciado_por__first_name__icontains=q)
                | Q(iniciado_por__last_name__icontains=q)
                | Q(iniciado_por__username__icontains=q)
                | Q(finalizado_por__first_name__icontains=q)
                | Q(finalizado_por__last_name__icontains=q)
            )

        # ── Filtro por status ──────────────────────
        status = params.get("status", "").strip()
        if status:
            qs = qs.filter(status=status)

        # ── Filtro por período ─────────────────────
        data_ini = params.get("data_ini", "").strip()
        data_fim = params.get("data_fim", "").strip()
        if data_ini:
            qs = qs.filter(iniciado_em__date__gte=data_ini)
        if data_fim:
            qs = qs.filter(iniciado_em__date__lte=data_fim)

        # ── Ordenação ─────────────────────────────
        ordem = params.get("ordem", "-iniciado_em").strip()
        ORDENS_PERMITIDAS = {
            "-iniciado_em",
            "iniciado_em",
            "receita__nome",
        }
        if ordem not in ORDENS_PERMITIDAS:
            ordem = "-iniciado_em"
        qs = qs.order_by(ordem)

        return qs

    # ─────────────────────────────────────────────
    # 📊 CONTEXTO
    # ─────────────────────────────────────────────

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Queryset completo da escola (sem filtros de URL) para as métricas
        qs_escola = self.get_base_queryset()

        # Contagens por status
        contagens = (
            qs_escola
            .values("status")
            .annotate(total=Count("id"))
        )
        status_map = {item["status"]: item["total"] for item in contagens}

        # Total de alunos atendidos (apenas execuções finalizadas)
        total_alunos = (
            qs_escola
            .filter(status="FINALIZADA")
            .aggregate(total=Sum("quantidade_alunos"))
            ["total"] or 0
        )

        context.update({
            "titulo_pagina": "Adaptação de Cardápio",

            # Métricas
            "total_execucoes":  qs_escola.count(),
            "total_finalizadas": status_map.get("FINALIZADA", 0),
            "total_em_preparo":  status_map.get("EM_PREPARO", 0),
            "total_canceladas":  status_map.get("CANCELADA", 0),
            "total_alunos":      total_alunos,
        })

        return context