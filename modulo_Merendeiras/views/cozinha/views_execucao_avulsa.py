"""
modulo_merendeiras/views_execucao_avulsa.py

View para execução avulsa de receita — independente do cardápio do dia.
A merendeira escolhe qualquer receita cujos ingredientes estejam disponíveis
no estoque da escola.
"""

from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from django import forms

from merendaEscolar.models import (
    Receita,
    ReceitaIngrediente,
    EstoqueEscola,
    MovimentacaoEstoque,
)
from modulo_Merendeiras.models import (
    ExecucaoReceitaCozinha,
    MovimentacaoCozinha,
)
from modulo_Merendeiras.views.cozinha.get_escola_da_merendeira import get_escola_da_merendeira as _get_escola_da_merendeira
from django.db.models import Q, Sum, Count
from django.views.generic import ListView


# ---------------------------------------------------------------------------
# Lógica de domínio
# ---------------------------------------------------------------------------

def _estoque_por_produto(escola):
    """
    Retorna dict {produto_id: Decimal(quantidade_total)} para a escola,
    considerando apenas lotes com quantidade > 0.
    """
    rows = (
        EstoqueEscola.objects
        .filter(escola=escola, quantidade__gt=0)
        .values('produto_id')
        .annotate(total=Sum('quantidade'))
    )
    return {row['produto_id']: row['total'] for row in rows}


def _receitas_executaveis(escola, porcoes=1):
    """
    Retorna lista de dicts com todas as receitas ativas,
    enriquecidas com disponibilidade de estoque para `porcoes` porções.

    Cada item:
        receita_id, receita_nome, rendimento_padrao,
        disponivel (bool),
        ingredientes: [{produto_id, produto_nome, unidade,
                        quantidade_base, quantidade_necessaria,
                        disponivel_estoque, suficiente}]
    """
    estoque_map = _estoque_por_produto(escola)
    receitas = (
        Receita.objects
        .filter(ativa=True)
        .prefetch_related('ingredientes__produto__unidade_medida')
        .order_by('nome')
    )

    resultado = []
    for receita in receitas:
        ingredientes_info = []
        receita_ok = True

        for ing in receita.ingredientes.all():
            qtd_base = ing.quantidade                          # por 1 porção
            qtd_nec  = qtd_base * Decimal(str(porcoes))
            disp     = estoque_map.get(ing.produto_id, Decimal('0'))
            suficiente = disp >= qtd_nec

            if not suficiente:
                receita_ok = False

            ingredientes_info.append({
                'produto_id':         ing.produto.id,
                'produto_nome':       ing.produto.nome,
                'unidade':            ing.produto.unidade_medida.sigla,
                'quantidade_base':    float(qtd_base),
                'quantidade_necessaria': float(qtd_nec),
                'disponivel_estoque': float(disp),
                'suficiente':         suficiente,
            })

        resultado.append({
            'receita_id':       receita.id,
            'receita_nome':     receita.nome,
            'rendimento_padrao': receita.rendimento,
            'disponivel':       receita_ok,
            'ingredientes':     ingredientes_info,
        })

    return resultado


# ---------------------------------------------------------------------------
# Form
# ---------------------------------------------------------------------------

class ExecucaoAvulsaForm(forms.Form):
    receita = forms.ModelChoiceField(
        queryset=Receita.objects.filter(ativa=True).order_by('nome'),
        label='Receita',
        widget=forms.Select(attrs={'class': 'form-select form-select-lg', 'id': 'id_receita'}),
    )
    quantidade_alunos = forms.IntegerField(
        min_value=1,
        max_value=9999,
        label='Número de alunos',
        widget=forms.NumberInput(attrs={
            'id': 'id_quantidade_alunos',
            'class': 'form-control form-control-lg',
            'placeholder': 'Ex: 120',
            'autocomplete': 'off',
        }),
    )
    turno = forms.ChoiceField(
        choices=(
            ('MANHA',    'Manhã'),
            ('TARDE',    'Tarde'),
            ('NOITE',    'Noite'),
            ('INTEGRAL', 'Integral'),
        ),
        label='Turno',
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'}),
    )
    observacoes = forms.CharField(
        required=False,
        label='Observações',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Motivo da substituição, adaptação, etc.',
        }),
    )


# ---------------------------------------------------------------------------
# View principal
# ---------------------------------------------------------------------------

from django.db import transaction
from django.core.exceptions import ValidationError
from core.views.baseMerendeira import BaseMerendeiraView




class ExecucaoAvulsaView(BaseMerendeiraView, FormView):
    """
    Permite à merendeira executar qualquer receita com estoque disponível,
    independentemente do cardápio do dia.

    Fluxo:
    1. Carrega todas as receitas ativas com indicação de disponibilidade.
    2. JS filtra/destaca com base no número de alunos digitado.
    3. Ao submeter, desconta ingredientes do estoque (FEFO) e registra execução.
    """
    template_name = 'modulo_merendeiras/cozinha/execucao_avulsa.html'
    form_class    = ExecucaoAvulsaForm
    success_url   = reverse_lazy('modulo_merendeiras:execucao_lista')

    def get_escola(self):
        return _get_escola_da_merendeira(self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        escola = self.get_escola()
        receitas = _receitas_executaveis(escola, porcoes=1)

        import json
        ctx['escola']       = escola
        ctx['hoje']         = timezone.now().date()
        ctx['receitas_info'] = receitas
        ctx['receitas_json'] = json.dumps(receitas)
        return ctx

    @transaction.atomic
    def form_valid(self, form):
        escola            = self.get_escola()
        receita           = form.cleaned_data['receita']
        quantidade_alunos = form.cleaned_data['quantidade_alunos']
        turno             = form.cleaned_data['turno']
        observacoes       = form.cleaned_data.get('observacoes', '')

        # Valida estoque antes de qualquer desconto
        estoque_map = _estoque_por_produto(escola)
        erros = []
        for ing in receita.ingredientes.select_related('produto__unidade_medida').all():
            qtd_nec = ing.quantidade * Decimal(str(quantidade_alunos))
            disp    = estoque_map.get(ing.produto_id, Decimal('0'))
            if disp < qtd_nec:
                falta = qtd_nec - disp
                erros.append(
                    f"{ing.produto.nome}: necessário {qtd_nec} {ing.produto.unidade_medida.sigla}, "
                    f"disponível {disp} {ing.produto.unidade_medida.sigla} "
                    f"(falta {falta:.2f})"
                )

        if erros:
            for e in erros:
                messages.error(self.request, e)
            return self.form_invalid(form)

        # Cria registro de execução
        execucao = ExecucaoReceitaCozinha.objects.create(
            escola=escola,
            receita=receita,
            status='EM_PREPARO',
            iniciado_por=self.request.user,
            quantidade_alunos=quantidade_alunos,
            observacoes=(
                f"[Execução avulsa — {turno}]"
                + (f"\n{observacoes}" if observacoes else "")
            ),
        )

        # Desconta estoque FEFO por ingrediente
        for ing in receita.ingredientes.select_related('produto__unidade_medida').all():
            qtd_restante = ing.quantidade * Decimal(str(quantidade_alunos))

            lotes = (
                EstoqueEscola.objects
                .select_for_update()
                .filter(escola=escola, produto=ing.produto, quantidade__gt=0)
                .order_by('data_validade', 'id')
            )

            for lote in lotes:
                if qtd_restante <= 0:
                    break

                consumir = min(lote.quantidade, qtd_restante)
                lote.quantidade -= consumir
                lote.save(update_fields=['quantidade'])

                MovimentacaoEstoque.objects.create(
                    produto=ing.produto,
                    escola=escola,
                    quantidade=consumir,
                    tipo='SAIDA_ESCOLA',
                    usuario=self.request.user,
                    observacao=(
                        f"Execução avulsa — {receita.nome} "
                        f"({quantidade_alunos} alunos / {turno}) "
                        f"| Lote: {lote.lote or 'S/L'} | Exec #{execucao.id}"
                    ),
                )

                MovimentacaoCozinha.objects.create(
                    escola=escola,
                    produto=ing.produto,
                    lote=lote.lote,
                    quantidade=consumir,
                    tipo='RETIRADA_RECEITA',
                    usuario=self.request.user,
                    execucao_receita=execucao,
                    observacao=f"Lote: {lote.lote} (Validade: {lote.data_validade})",
                )

                qtd_restante -= consumir

        execucao.finalizar(self.request.user, rendimento_real=quantidade_alunos)

        messages.success(
            self.request,
            f'✅ Receita "{receita.nome}" executada para {quantidade_alunos} alunos!'
        )
        return super().form_valid(form)
    



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
            "titulo_pagina": "Execuções Avulsas de Receita",

            # Métricas
            "total_execucoes":  qs_escola.count(),
            "total_finalizadas": status_map.get("FINALIZADA", 0),
            "total_em_preparo":  status_map.get("EM_PREPARO", 0),
            "total_canceladas":  status_map.get("CANCELADA", 0),
            "total_alunos":      total_alunos,
        })

        return context