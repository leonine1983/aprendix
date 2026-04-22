from django.views.generic import TemplateView
from django.utils import timezone
from django.db import transaction

from ..baseMerendeiraView import BaseMerendeiraView
from merendaEscolar.models import Cardapio, CardapioSemana, CardapioDia, CardapioItem
from modulo_Merendeiras.models import (
    ExecucaoCardapioDia,
    # services
    executar_cardapio_do_dia,
    verificar_disponibilidade_ingredientes,
)

from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.utils import timezone
from django.db import transaction

from ..baseMerendeiraView import BaseMerendeiraView
from merendaEscolar.models import Cardapio, CardapioSemana, CardapioDia, CardapioItem
from modulo_Merendeiras.models import (
    ExecucaoCardapioDia,
    executar_cardapio_do_dia,
    verificar_disponibilidade_ingredientes,
)

from django.shortcuts import redirect
from django.contrib import messages


class PrepararExecucaoView(BaseMerendeiraView, TemplateView):
    template_name = "modulo_merendeiras/cadapioHoje/preparar_execucao.html"

    TURNOS_DISPONIVEIS = [
        ("MANHA",    "Manhã"),
        ("TARDE",    "Tarde"),
        ("NOITE",    "Noite"),
        ("INTEGRAL", "Integral"),
    ]

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

        total_semanas = CardapioSemana.objects.filter(cardapio=cardapio).count()
        if numero_semana > total_semanas:
            return None

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

    def _get_quantidade_alunos_por_turno(self, escola, hoje):
        try:
            from gestao_escolar.models import Matriculas
            from django.db.models import Count

            matriculas = Matriculas.objects.filter(
                turma__escola=escola,
                turma__ano_letivo__ativo=True,
                desistente=False,
                transferido=False,
            ).select_related('turma')

            if not matriculas.exists():
                return None

            por_turno = (
                matriculas
                .values('turma__turno')
                .annotate(total=Count('id'))
                .order_by('turma__turno')
            )

            turnos = {item['turma__turno']: item['total'] for item in por_turno}
            total = sum(turnos.values())

            return {'por_turno': turnos, 'total': total, 'fonte': 'matriculas'}

        except Exception:
            return None

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

        max_porcoes = int(min_ratio * rendimento_base)
        return min(max_porcoes, 1000)

     # ── GET ────────────────────────────────────────────────────────
    def get(self, request, *args, **kwargs):
        escola = self.get_escola_usuario()
        hoje   = timezone.now().date()

        if not escola:
            messages.error(request, "Escola não encontrada.")
            return redirect('modulo_merendeiras:cardapio_hoje')

        cardapio_dia = self.get_cardapio_do_dia(escola, hoje)
        if not cardapio_dia:
            messages.error(request, "Não há cardápio planejado para hoje.")
            return redirect('modulo_merendeiras:cardapio_hoje')

        # Verifica quais turnos JÁ foram executados hoje
        turnos_executados = set(
            ExecucaoCardapioDia.objects
            .filter(escola=escola, data=hoje)
            .values_list('turno', flat=True)
        )

        # Se TODOS os turnos foram executados, bloqueia
        todos = {t[0] for t in self.TURNOS_DISPONIVEIS}
        if turnos_executados >= todos:
            messages.warning(request, "Todos os turnos já foram executados hoje.")
            return redirect('modulo_merendeiras:cardapio_hoje')

        return super().get(request, *args, **kwargs)

    # ── get_context_data ───────────────────────────────────────────
    def get_context_data(self, **kwargs):
        ctx   = super().get_context_data(**kwargs)
        escola = self.get_escola_usuario()
        hoje   = timezone.now().date()

        cardapio_dia = self.get_cardapio_do_dia(escola, hoje)

        # Turnos já executados hoje
        turnos_executados = set(
            ExecucaoCardapioDia.objects
            .filter(escola=escola, data=hoje)
            .values_list('turno', flat=True)
        )

        # Monta lista de turnos disponíveis (não executados ainda)
        turnos_disponiveis = [
            {'valor': v, 'label': l}
            for v, l in self.TURNOS_DISPONIVEIS
            if v not in turnos_executados
        ]

        itens = CardapioItem.objects.filter(
            dia=cardapio_dia
        ).select_related('receita', 'tipo_refeicao')

        itens_preparados = []
        for item in itens:
            rendimento_padrao = getattr(item.receita, 'rendimento', 100)
            disponivel, info  = verificar_disponibilidade_ingredientes(
                escola, item.receita, rendimento_padrao
            )
            maximo_calculado = self._calcular_maximo_porcoes(info, rendimento_padrao)
            if maximo_calculado == 0 and disponivel:
                maximo_calculado = 1000

            itens_preparados.append({
                'item': item,
                'estoque_ok': disponivel,
                'porcoes_sugeridas': rendimento_padrao,
                'porcoes_maximas': maximo_calculado,
                'faltantes': info.get('faltantes', []),
                'ingredientes': info['ingredientes'],
            })

        dados_alunos = self._get_quantidade_alunos_por_turno(escola, hoje)

        ctx.update({
            'cardapio': cardapio_dia,
            'itens': itens_preparados,
            'hoje': hoje,
            'total_itens': len(itens_preparados),
            'itens_com_estoque': sum(1 for i in itens_preparados if i['estoque_ok']),
            'turnos_disponiveis': turnos_disponiveis,        # ← NOVO
            'turnos_executados': list(turnos_executados),    # ← NOVO (para exibir no template)
            'quantidade_alunos': dados_alunos['total'] if dados_alunos else None,
            'alunos_por_turno': dados_alunos['por_turno'] if dados_alunos else None,
            'alunos_fonte_matriculas': dados_alunos is not None,
        })

        return ctx

    # ── POST ───────────────────────────────────────────────────────
    def post(self, request, *args, **kwargs):
        escola = self.get_escola_usuario()
        hoje   = timezone.now().date()

        if not escola:
            messages.error(request, "Escola não encontrada.")
            return redirect('modulo_merendeiras:cardapio_hoje')

        # ── Valida turno ────────────────────────────────────────────
        turno = request.POST.get('turno', '').strip()
        turnos_validos = {t[0] for t in self.TURNOS_DISPONIVEIS}

        if turno not in turnos_validos:
            messages.error(request, "Turno inválido. Selecione um turno válido.")
            return redirect('modulo_merendeiras:preparar_execucao')

        if ExecucaoCardapioDia.objects.filter(escola=escola, data=hoje, turno=turno).exists():
            messages.warning(request, f"O turno {turno} já foi executado hoje.")
            return redirect('modulo_merendeiras:preparar_execucao')

        # ── Porções ─────────────────────────────────────────────────
        porcoes_override = {}
        for key, value in request.POST.items():
            if key.startswith('porcoes_'):
                try:
                    receita_id = int(key.replace('porcoes_', ''))
                    porcoes_override[receita_id] = int(value)
                except ValueError:
                    pass

        cardapio_dia = self.get_cardapio_do_dia(escola, hoje)
        if not cardapio_dia:
            messages.error(request, "Cardápio não encontrado.")
            return redirect('modulo_merendeiras:cardapio_hoje')

        quantidade_alunos_manual = None
        try:
            val = int(request.POST.get('quantidade_alunos_manual', 0))
            if val > 0:
                quantidade_alunos_manual = val
        except (ValueError, TypeError):
            pass

        try:
            with transaction.atomic():
                resultado = executar_cardapio_do_dia(
                    escola=escola,
                    data=hoje,
                    usuario=request.user,
                    cardapio_dia=cardapio_dia,
                    porcoes_override=porcoes_override or None,
                    quantidade_alunos=quantidade_alunos_manual,
                    turno=turno,   # ← repasse para o service
                )

                execucao_id = resultado['execucao_dia_id']

                if resultado['sucessos']:
                    msg = (
                        f"Cardápio do turno {turno} executado! "
                        f"{len(resultado['sucessos'])} receita(s) preparada(s)."
                    )
                    if resultado['falhas']:
                        msg += f" ({len(resultado['falhas'])} falha(s))"
                    messages.success(request, msg)
                else:
                    messages.error(request, "Não foi possível executar nenhuma receita.")

                return redirect('modulo_merendeiras:execucao_detalhe', pk=execucao_id)

        except Exception as e:
            messages.error(request, f"Erro ao executar cardápio: {str(e)}")
            return redirect('modulo_merendeiras:cardapio_hoje')