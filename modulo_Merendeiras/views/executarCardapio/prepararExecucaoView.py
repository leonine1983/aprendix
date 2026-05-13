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
    cardapio_dia=None,
    quantidade_alunos=None,
    criar_execucao_receita=True,   # ← novo parâmetro
):
    from modulo_Merendeiras.models import (
        ExecucaoReceitaCozinha,
        ExecucaoCardapioItem,
        MovimentacaoCozinha,
    )
    from merendaEscolar.models import TipoRefeicao, CardapioItem

    receita = Receita.objects.get(id=receita_id)

    disponivel, info = verificar_disponibilidade_ingredientes(escola, receita, porcoes)
    if not disponivel:
        raise Exception("Estoque insuficiente para esta quantidade.")

    # --- execução do dia (mestre) ---
    execucao_dia, created = ExecucaoCardapioDia.objects.get_or_create(
        escola=escola,
        data=data,
        turno=turno,
        defaults={
            'executado_por': usuario,
            'quantidade_alunos': quantidade_alunos,
            'status': 'EM_EXECUCAO',
            'cardapio_dia': cardapio_dia,
        }
    )

    if cardapio_dia and not execucao_dia.cardapio_dia:
        execucao_dia.cardapio_dia = cardapio_dia
        execucao_dia.save(update_fields=['cardapio_dia'])

    if not created and quantidade_alunos and not execucao_dia.quantidade_alunos:
        execucao_dia.quantidade_alunos = quantidade_alunos
        execucao_dia.save(update_fields=['quantidade_alunos'])

    # --- execução da receita (opcional) ---
    exec_receita = None
    if criar_execucao_receita:
        exec_receita = ExecucaoReceitaCozinha.objects.create(
            escola=escola,
            receita=receita,
            status='EM_PREPARO',
            iniciado_por=usuario,
        )

    # --- baixa estoque (FEFO) ---
    for ing in receita.ingredientes.all():
        quantidade_necessaria = ing.quantidade * porcoes

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
            consumir = min(estoque.quantidade, restante)
            estoque.quantidade -= consumir
            estoque.save(update_fields=['quantidade'])
            restante -= consumir

            MovimentacaoCozinha.objects.create(
                escola=escola,
                produto=ing.produto,
                lote=estoque.lote,
                quantidade=consumir,
                tipo='RETIRADA_RECEITA',
                usuario=usuario,
                execucao_receita=exec_receita,   # será None se criar_execucao_receita=False
                observacao=(
                    f"Lote: {estoque.lote} "
                    f"(Validade: {estoque.data_validade})"
                )
            )

        if restante > 0:
            raise Exception(f"Erro ao debitar estoque de {ing.produto.nome}")

    # --- finaliza execução da receita (apenas se foi criada) ---
    if exec_receita:
        exec_receita.status = 'FINALIZADA'
        exec_receita.finalizado_em = timezone.now()
        exec_receita.finalizado_por = usuario
        exec_receita.rendimento_real = porcoes
        exec_receita.save(
            update_fields=['status', 'finalizado_em', 'finalizado_por', 'rendimento_real']
        )

    # --- descobre tipo de refeição ---
    tipo_refeicao = None
    if execucao_dia.cardapio_dia:
        ci = CardapioItem.objects.filter(
            dia=execucao_dia.cardapio_dia,
            receita=receita
        ).select_related('tipo_refeicao').first()
        if ci:
            tipo_refeicao = ci.tipo_refeicao

    if not tipo_refeicao:
        tipo_refeicao = TipoRefeicao.objects.first()

    if not tipo_refeicao:
        raise Exception("Nenhum TipoRefeicao cadastrado no sistema.")

    # --- item executado do cardápio ---
    exec_item, item_created = ExecucaoCardapioItem.objects.get_or_create(
        execucao_cardapio=execucao_dia,
        receita=receita,
        tipo_refeicao=tipo_refeicao,
        defaults={
            'execucao_receita': exec_receita,
            'status': 'EXECUTADO',
            'porcoes_planejadas': porcoes,
            'porcoes_executadas': porcoes,
        }
    )

    if not item_created:
        alterou = False
        if exec_receita and not exec_item.execucao_receita:
            exec_item.execucao_receita = exec_receita
            alterou = True
        if exec_item.status != 'EXECUTADO':
            exec_item.status = 'EXECUTADO'
            alterou = True
        if not exec_item.porcoes_executadas:
            exec_item.porcoes_executadas = porcoes
            alterou = True
        if alterou:
            exec_item.save()

    # --- status final do dia ---
    total_itens = execucao_dia.itens_executados.count()
    total_executados = execucao_dia.itens_executados.filter(status='EXECUTADO').count()

    if total_itens > 0:
        execucao_dia.status = 'EXECUTADO' if total_executados == total_itens else 'PARCIAL'
        execucao_dia.finalizado_em = timezone.now()
        execucao_dia.save(update_fields=['status', 'finalizado_em'])

    return {
        'execucao_id': execucao_dia.id,
        'receita': receita.nome,
        'porcoes': porcoes,
        'turno': turno,
        'cardapio_dia_id': execucao_dia.cardapio_dia.id if execucao_dia.cardapio_dia else None,
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

        turnos_validos = {t[0] for t in self.TURNOS_DISPONIVEIS}
        if turno not in turnos_validos:
            messages.error(request, "Turno inválido.")
            return redirect('modulo_merendeiras:preparar_execucao')

        try:
            porcoes = int(request.POST.get(f'porcoes_{receita_id}', 0))
        except ValueError:
            porcoes = 0

        if porcoes <= 0:
            messages.error(request, "Informe ao menos 1 porção.")
            return redirect('modulo_merendeiras:preparar_execucao')

        # ✅ BUSCA O CARDÁPIO ANTES DE EXECUTAR
        cardapio_dia = self.get_cardapio_do_dia(escola, hoje)
        if not cardapio_dia:
            messages.error(request, "Não há cardápio vinculado para hoje.")
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
                    cardapio_dia=cardapio_dia,
                    criar_execucao_receita=False,   # ← sem ExecucaoReceitaCozinha
                )
                messages.success(
                    request,
                    f"Receita executada com sucesso ({porcoes} porções - {turno})."
                )
                from django.utils.safestring import mark_safe
                from django.urls import reverse
                url_execucoes = reverse('modulo_merendeiras:lista_execucoes')
                messages.info(
                    request,
                    mark_safe(f""" <div style="
    margin-top:12px;
    padding:16px;
    border:1px solid #dbeafe;
    border-radius:14px;
    background:#f8fbff;
    color:#1e293b;
    line-height:1.6;
">

    <div style="
        font-size:15px;
        font-weight:600;
        margin-bottom:12px;
        color:#0f172a;
    ">
        📋 Ficha Diária – Controle da Alimentação Escolar
    </div>

    <div style="margin-bottom:14px;">
        Após servir a alimentação aos alunos, acesse a área de execuções
        para preencher a ficha diária referente ao cardápio executado,
        informando os dados da refeição servida conforme a data e o turno.
    </div>

    <a href="{url_execucoes}"
       style="
            text-decoration:none;
            display:inline-block;
       ">

        <div style="
            display:flex;
            align-items:center;
            gap:8px;
            padding:10px 14px;
            border:1px solid #cbd5e1;
            border-radius:10px;
            background:#ffffff;
            width:max-content;
            font-weight:600;
            color:#334155;
            transition:all .2s ease;
            cursor:pointer;
        ">

            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M3 2h2l2.5 9H18l2-7H7"
                      stroke="currentColor"
                      stroke-width="1.8"
                      stroke-linecap="round"
                      stroke-linejoin="round"/>
                <circle cx="9" cy="20" r="1.5"
                        stroke="currentColor"
                        stroke-width="1.8"/>
                <circle cx="17" cy="20" r="1.5"
                        stroke="currentColor"
                        stroke-width="1.8"/>
            </svg>

            <span class="sb-item__label">
                Execuções
            </span>
        </div>
    </a>

    <div style="
        margin-top:14px;
        font-size:14px;
        color:#475569;
    ">
        Em seguida, localize a execução desejada pela
        <strong>data</strong> e pelo
        <strong>turno</strong>,
        e preencha a ficha correspondente.
    </div>

</div>
                    """)
                )

        except Exception as e:
            messages.error(request, f"Erro: {str(e)}")


        return redirect('modulo_merendeiras:preparar_execucao')