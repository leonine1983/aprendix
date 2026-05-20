"""
modulo_merendeiras/views_execucao_avulsa.py

View para execução avulsa de receita — independente do cardápio do dia.
A merendeira escolhe qualquer receita cujos ingredientes estejam disponíveis
no estoque da escola.
"""

from decimal import Decimal
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from django import forms

from merendaEscolar.models import (
    Receita,
    EstoqueEscola,
    MovimentacaoEstoque,
)
from modulo_Merendeiras.models import (
    ExecucaoReceitaCozinha,
    MovimentacaoCozinha,
)
from modulo_Merendeiras.views.cozinha.get_escola_da_merendeira import get_escola_da_merendeira as _get_escola_da_merendeira
from django.db.models import  Sum

from django.db import transaction
from core.views.baseMerendeira import BaseMerendeiraView


# ---------------------------------------------------------------------------
# Lógica de domínio
# ---------------------------------------------------------------------------
def _estoque_por_produto(escola):
    """
    Retorna um dicionário no formato:
        {produto_id: quantidade_total}

    Considera apenas os lotes da escola com quantidade maior que zero.
    """
    if not escola:
        return {}

    rows = (
        EstoqueEscola.objects
        .filter(
            escola=escola,
            quantidade__gt=0,
        )
        .values('produto_id')
        .annotate(total=Sum('quantidade'))
    )

    return {
        row['produto_id']: row['total']
        for row in rows
    }


def _receitas_executaveis(escola, porcoes=1):
    """
    Retorna uma lista com todas as receitas ativas, indicando se cada uma
    pode ser executada com base no estoque disponível da escola.

    Estrutura retornada:
        [
            {
                'receita_id': 1,
                'receita_nome': 'Arroz Doce',
                'rendimento_padrao': 100,
                'disponivel': True,
                'ingredientes': [
                    {
                        'produto_id': 3,
                        'produto_nome': 'Arroz',
                        'unidade': 'kg',
                        'quantidade_base': 0.200,
                        'quantidade_necessaria': 0.200,
                        'disponivel_estoque': 5.0,
                        'suficiente': True,
                    },
                ],
            },
        ]
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
            qtd_base = ing.quantidade
            qtd_necessaria = qtd_base * Decimal(str(porcoes))
            qtd_disponivel = estoque_map.get(
                ing.produto_id,
                Decimal('0')
            )

            suficiente = qtd_disponivel >= qtd_necessaria

            if not suficiente:
                receita_ok = False

            ingredientes_info.append({
                'produto_id': ing.produto_id,
                'produto_nome': ing.produto.nome,
                'unidade': ing.produto.unidade_medida.sigla,
                'quantidade_base': float(qtd_base),
                'quantidade_necessaria': float(qtd_necessaria),
                'disponivel_estoque': float(qtd_disponivel),
                'suficiente': suficiente,
            })

        resultado.append({
            'receita_id': receita.id,
            'receita_nome': receita.nome,
            'rendimento_padrao': receita.rendimento,
            'disponivel': receita_ok,
            'ingredientes': ingredientes_info,
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

class ExecucaoAvulsaView(BaseMerendeiraView, FormView):
    """
    Permite à merendeira executar qualquer receita com estoque disponível,
    independentemente do cardápio do dia.
    """

    template_name = 'modulo_merendeiras/cozinha/execucao_avulsa.html'
    form_class = ExecucaoAvulsaForm
    success_url = reverse_lazy('modulo_merendeiras:execucao_lista')

    def get_escola(self):
        """
        Retorna a escola vinculada à merendeira utilizando a infraestrutura
        já disponibilizada pela BaseMerendeiraView.
        """
        return self.escola_usuario

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        escola = self.get_escola()

        # Importante:
        # _receitas_executaveis(escola, porcoes=1) deve retornar
        # quantidade_base = quantidade necessária para 1 porção/aluno.
        # O JavaScript do template será responsável por recalcular
        # as quantidades conforme o número de alunos informado.
        receitas = _receitas_executaveis(escola, porcoes=1)

        # Ordena receitas disponíveis primeiro
        receitas = sorted(
            receitas,
            key=lambda r: (0 if r['disponivel'] else 1, r['receita_nome'])
        )

        import json

        ctx['escola'] = escola
        ctx['hoje'] = timezone.now().date()
        ctx['receitas_info'] = receitas
        ctx['receitas_json'] = json.dumps(
            receitas,
            ensure_ascii=False
        )

        return ctx

    @transaction.atomic
    def form_valid(self, form):
        escola = self.get_escola()

        receita = form.cleaned_data['receita']
        quantidade_alunos = form.cleaned_data['quantidade_alunos']
        turno = form.cleaned_data['turno']
        observacoes = form.cleaned_data.get('observacoes', '')

        estoque_map = _estoque_por_produto(escola)

        erros = []
        for ing in receita.ingredientes.select_related(
            'produto__unidade_medida'
        ).all():
            qtd_nec = ing.quantidade * Decimal(str(quantidade_alunos))
            disp = estoque_map.get(ing.produto_id, Decimal('0'))

            if disp < qtd_nec:
                falta = qtd_nec - disp
                erros.append(
                    f"{ing.produto.nome}: necessário {qtd_nec} "
                    f"{ing.produto.unidade_medida.sigla}, "
                    f"disponível {disp} "
                    f"{ing.produto.unidade_medida.sigla} "
                    f"(falta {falta:.2f})"
                )

        if erros:
            for erro in erros:
                messages.error(self.request, erro)
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

        # Consumo FEFO por ingrediente
        for ing in receita.ingredientes.select_related(
            'produto__unidade_medida'
        ).all():
            qtd_restante = (
                ing.quantidade * Decimal(str(quantidade_alunos))
            )

            lotes = (
                EstoqueEscola.objects
                .select_for_update()
                .filter(
                    escola=escola,
                    produto=ing.produto,
                    quantidade__gt=0
                )
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
                        f"| Lote: {lote.lote or 'S/L'} "
                        f"| Exec #{execucao.id}"
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
                    observacao=(
                        f"Lote: {lote.lote} "
                        f"(Validade: {lote.data_validade})"
                    ),
                )

                qtd_restante -= consumir

        execucao.finalizar(
            self.request.user,
            rendimento_real=quantidade_alunos
        )

        messages.success(
            self.request,
            f'✅ Receita "{receita.nome}" executada para '
            f'{quantidade_alunos} alunos!'
        )

        return super().form_valid(form)
