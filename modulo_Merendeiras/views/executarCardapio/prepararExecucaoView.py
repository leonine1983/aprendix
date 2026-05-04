from django.views.generic import TemplateView
from django.utils import timezone
from django.db import transaction
from django.shortcuts import redirect
from django.contrib import messages

from ..baseMerendeiraView import BaseMerendeiraView
from merendaEscolar.models import Cardapio, CardapioSemana, CardapioDia, CardapioItem, Receita

from modulo_Merendeiras.models import (
    ExecucaoCardapioDia,
    verificar_disponibilidade_ingredientes,
)

from django.views.generic import TemplateView
from django.utils import timezone
from django.db import transaction
from django.shortcuts import redirect
from django.contrib import messages

from ..baseMerendeiraView import BaseMerendeiraView
from merendaEscolar.models import (
    Cardapio, CardapioSemana, CardapioDia, CardapioItem, Receita, EstoqueEscola
)

from modulo_Merendeiras.models import (
    ExecucaoCardapioDia,
    verificar_disponibilidade_ingredientes,
)


from django.db import transaction
from django.utils import timezone
from merendaEscolar.models import Receita
from modulo_Merendeiras.models import ExecucaoCardapioDia


@transaction.atomic
def executar_receita_individual(
    escola,
    data,
    usuario,
    receita_id,
    porcoes,
    turno,
    quantidade_alunos=None
):

    receita = Receita.objects.get(id=receita_id)

    # 🔍 valida disponibilidade
    disponivel, info = verificar_disponibilidade_ingredientes(
        escola, receita, porcoes
    )

    if not disponivel:
        raise Exception("Estoque insuficiente para esta quantidade.")

    # ✅ cria OU reutiliza execução do turno (resolve UNIQUE)
    execucao, created = ExecucaoCardapioDia.objects.get_or_create(
        escola=escola,
        data=data,
        turno=turno,
        defaults={
            'executado_por': usuario,
            'quantidade_alunos': quantidade_alunos
        }
    )

    # 🔥 baixa estoque REAL (FEFO)
    for ing in receita.ingredientes.all():

        quantidade_necessaria = ing.quantidade * porcoes

        # pega lotes ordenados por validade (FEFO)
        estoques = EstoqueEscola.objects.filter(
            escola=escola,
            produto=ing.produto,
            quantidade__gt=0,
            data_validade__gte=timezone.now().date()
        ).order_by('data_validade')

        restante = quantidade_necessaria

        for estoque in estoques:
            if restante <= 0:
                break

            if estoque.quantidade >= restante:
                estoque.quantidade -= restante
                estoque.save()
                restante = 0
            else:
                restante -= estoque.quantidade
                estoque.quantidade = 0
                estoque.save()

        # segurança extra (não deveria acontecer se validou antes)
        if restante > 0:
            raise Exception(f"Erro ao debitar estoque de {ing.produto.nome}")

    return {
        'execucao_id': execucao.id,
        'receita': receita.nome,
        'porcoes': porcoes
    }


class PrepararExecucaoView(BaseMerendeiraView, TemplateView):
    template_name = "modulo_merendeiras/cadapioHoje/preparar_execucao.html"

    TURNOS_DISPONIVEIS = [
        ("MANHA", "Manhã"),
        ("TARDE", "Tarde"),
        ("NOITE", "Noite"),
        ("INTEGRAL", "Integral"),
    ]

    # ─────────────────────────────────────────────
    def get_cardapio_do_dia(self, escola, hoje):
        dia_semana = hoje.isoweekday()
        if dia_semana > 5:
            return None

        cardapio = Cardapio.objects.filter(
            cardapioescola__escola=escola,
            ativo=True,
            data_inicio__lte=hoje,
            data_fim__gte=hoje
        ).first()

        if not cardapio:
            return None

        dias_desde_inicio = (hoje - cardapio.data_inicio).days
        numero_semana = (dias_desde_inicio // 7) + 1

        semana = CardapioSemana.objects.filter(
            cardapio=cardapio,
            numero=numero_semana
        ).first()

        if not semana:
            return None

        return CardapioDia.objects.filter(
            semana=semana,
            dia_semana=dia_semana
        ).first()

    # ─────────────────────────────────────────────
    def _calcular_maximo_porcoes(self, detalhes, rendimento_base=100):
        if not detalhes or not detalhes.get('ingredientes'):
            return rendimento_base

        min_ratio = float('inf')

        for ing in detalhes['ingredientes']:
            necessario = ing.get('necessario', 0)
            disponivel = ing.get('disponivel', 0)

            if necessario > 0:
                ratio = disponivel / necessario
                if ratio < min_ratio:
                    min_ratio = ratio

        if min_ratio == float('inf'):
            return rendimento_base

        return min(int(min_ratio * rendimento_base), 1000)

    # ─────────────────────────────────────────────
    def get(self, request, *args, **kwargs):
        escola = self.get_escola_usuario()
        hoje = timezone.now().date()

        if not escola:
            messages.error(request, "Escola não encontrada.")
            return redirect('modulo_merendeiras:cardapio_hoje')

        if not self.get_cardapio_do_dia(escola, hoje):
            messages.error(request, "Não há cardápio para hoje.")
            return redirect('modulo_merendeiras:cardapio_hoje')

        return super().get(request, *args, **kwargs)

    # ─────────────────────────────────────────────
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        escola = self.get_escola_usuario()
        hoje = timezone.now().date()
        cardapio_dia = self.get_cardapio_do_dia(escola, hoje)

        itens = CardapioItem.objects.filter(
            dia=cardapio_dia
        ).select_related('receita', 'tipo_refeicao')

        itens_preparados = []

        for item in itens:
            rendimento = getattr(item.receita, 'rendimento', 100)

            disponivel, info = verificar_disponibilidade_ingredientes(
                escola, item.receita, rendimento
            )

            maximo = self._calcular_maximo_porcoes(info, rendimento)

            itens_preparados.append({
                'item': item,
                'estoque_ok': disponivel,
                'porcoes_sugeridas': rendimento,
                'porcoes_maximas': maximo,
                'faltantes': info.get('faltantes', []),
                'ingredientes': info['ingredientes'],
            })

        ctx.update({
            'cardapio': cardapio_dia,
            'itens': itens_preparados,
            'hoje': hoje,
            'total_itens': len(itens_preparados),
            'itens_com_estoque': sum(1 for i in itens_preparados if i['estoque_ok']),
            'turnos_disponiveis': [
                {'valor': v, 'label': l} for v, l in self.TURNOS_DISPONIVEIS
            ],
            'porcoes_presets': [100, 200, 300, 500],
        })

        return ctx

    # ─────────────────────────────────────────────
    def post(self, request, *args, **kwargs):
        escola = self.get_escola_usuario()
        hoje = timezone.now().date()

        if not escola:
            messages.error(request, "Escola não encontrada.")
            return redirect('modulo_merendeiras:cardapio_hoje')

        receita_id = request.POST.get('receita_id')
        turno = request.POST.get('turno')

        if not receita_id:
            messages.error(request, "Receita não informada.")
            return redirect('modulo_merendeiras:preparar_execucao')

        if not turno:
            messages.error(request, "Selecione o turno.")
            return redirect('modulo_merendeiras:preparar_execucao')

        # valida turno
        turnos_validos = {t[0] for t in self.TURNOS_DISPONIVEIS}
        if turno not in turnos_validos:
            messages.error(request, "Turno inválido.")
            return redirect('modulo_merendeiras:preparar_execucao')

        # pega porções
        try:
            porcoes = int(request.POST.get(f'porcoes_{receita_id}', 0))
        except ValueError:
            porcoes = 0

        if porcoes <= 0:
            messages.error(request, "Informe ao menos 1 porção.")
            return redirect('modulo_merendeiras:preparar_execucao')

        try:
            with transaction.atomic():

                executar_receita_individual(
                    escola=escola,
                    data=hoje,
                    usuario=request.user,
                    receita_id=int(receita_id),
                    porcoes=porcoes,
                    turno=turno,
                )

                messages.success(
                    request,
                    f"Receita executada com sucesso ({porcoes} porções - {turno})."
                )

        except Exception as e:
            messages.error(request, f"Erro: {str(e)}")

        return redirect('modulo_merendeiras:preparar_execucao')