from django.views.generic import ListView, DetailView, TemplateView, View
from django.views.generic.edit import FormMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse
from datetime import date, timedelta

from ..baseMerendeiraView import BaseMerendeiraView
from merendaEscolar.models import CardapioDia, CardapioItem
from modulo_Merendeiras.models import (
    ExecucaoCardapioDia,
    ExecucaoCardapioItem,
    ExecucaoReceitaCozinha,
    # services
    executar_cardapio_do_dia,
    verificar_disponibilidade_ingredientes,
    EstoqueInsuficienteError,
)

from django.views.generic import ListView, DetailView, TemplateView, View
from django.views.generic.edit import FormMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse
from datetime import date, timedelta

from ..baseMerendeiraView import BaseMerendeiraView
from merendaEscolar.models import CardapioDia, CardapioItem, CardapioSemana
from modulo_Merendeiras.models import (
    ExecucaoCardapioDia,
    ExecucaoCardapioItem,
    ExecucaoReceitaCozinha,
    # services
    executar_cardapio_do_dia,
    verificar_disponibilidade_ingredientes,
    EstoqueInsuficienteError,
)


class CardapioHojeView(BaseMerendeiraView, TemplateView):
    """
    Dashboard principal: mostra o cardápio do dia atual e status de execução.
    """
    template_name = "modulo_merendeiras/cadapioHoje/cardapio_hoje.html"
    
    # modulo_Merendeiras/views/executarCardapio/executaCardapio.py

    # modulo_Merendeiras/views/executarCardapio/executaCardapio.py

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        escola = self.get_escola_usuario()
        
        if not escola:
            messages.error(self.request, "Você não está vinculada a nenhuma escola.")
            return ctx
        
        hoje = timezone.now().date()
        
        # Busca cardápio planejado para hoje
        cardapio_hoje = self.get_cardapio_do_dia(escola, hoje)
        
        # Busca execução existente
        execucao_existente = ExecucaoCardapioDia.objects.filter(
            escola=escola,
            data=hoje
        ).prefetch_related('itens_executados__receita', 'itens_executados__tipo_refeicao').first()
        
        # Prepara dados do cardápio
        itens_cardapio = []
        if cardapio_hoje and not execucao_existente:
            itens = CardapioItem.objects.filter(
                dia=cardapio_hoje  # ✅ CORRIGIDO: campo é 'dia', não 'cardapio_dia'
            ).select_related('receita', 'tipo_refeicao')
            
            for item in itens:
                disponivel, info = verificar_disponibilidade_ingredientes(
                    escola, item.receita, item.receita.rendimento
                )
                item.estoque_ok = disponivel
                item.detalhes_estoque = info
                itens_cardapio.append(item)
        
        ctx.update({
            'hoje': hoje,
            'cardapio': cardapio_hoje,
            'execucao': execucao_existente,
            'itens_cardapio': itens_cardapio,
            'pode_executar': cardapio_hoje and not execucao_existente and itens_cardapio,
            'escola': escola,
        })
        
        return ctx


    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        escola = self.get_escola_usuario()
        
        if not escola:
            messages.error(self.request, "Você não está vinculada a nenhuma escola.")
            return ctx
        
        hoje = timezone.now().date()
        
        # Busca cardápio planejado para hoje (pelo dia da semana)
        cardapio_hoje = self.get_cardapio_do_dia(escola, hoje)
        
        # Busca execução existente (se já foi iniciada)
        execucao_existente = ExecucaoCardapioDia.objects.filter(
            escola=escola,
            data=hoje
        ).prefetch_related('itens_executados__receita', 'itens_executados__tipo_refeicao').first()
        
        # Prepara dados do cardápio com verificação de estoque
        itens_cardapio = []
        if cardapio_hoje and not execucao_existente:
            itens = CardapioItem.objects.filter(
                cardapio_dia=cardapio_hoje
            ).select_related('receita', 'tipo_refeicao')
            
            for item in itens:
                disponivel, info = verificar_disponibilidade_ingredientes(
                    escola, item.receita, item.receita.rendimento
                )
                item.estoque_ok = disponivel
                item.detalhes_estoque = info
                itens_cardapio.append(item)
        
        ctx.update({
            'hoje': hoje,
            'cardapio': cardapio_hoje,
            'execucao': execucao_existente,
            'itens_cardapio': itens_cardapio,
            'pode_executar': cardapio_hoje and not execucao_existente and itens_cardapio,
            'escola': escola,
        })
        
        return ctx


class PrepararExecucaoView(BaseMerendeiraView, TemplateView):
    """
    Tela de preparação: permite ajustar quantidades antes de executar.
    """
    template_name = "modulo_merendeiras/cardapio/preparar_execucao.html"
    
    def get_cardapio_do_dia(self, escola, hoje):
        """Busca cardápio pelo dia da semana"""
        dia_semana = hoje.isoweekday()
        
        semana = CardapioSemanal.objects.filter(
            escola=escola,
            ativo=True
        ).first()
        
        if not semana:
            return None
            
        return CardapioDia.objects.filter(
            semana=semana,
            dia_semana=dia_semana
        ).first()
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        escola = self.get_escola_usuario()
        hoje = timezone.now().date()
        
        if not escola:
            messages.error(self.request, "Escola não encontrada.")
            return redirect('modulo_merendeiras:cardapio_hoje')
        
        # Verifica se já existe execução
        if ExecucaoCardapioDia.objects.filter(escola=escola, data=hoje).exists():
            messages.warning(self.request, "O cardápio de hoje já foi executado.")
            return redirect('modulo_merendeiras:cardapio_hoje')
        
        # Busca itens do cardápio
        cardapio = self.get_cardapio_do_dia(escola, hoje)
        
        if not cardapio:
            messages.error(self.request, "Não há cardápio planejado para hoje.")
            return redirect('modulo_merendeiras:cardapio_hoje')
        
        itens = CardapioItem.objects.filter(
            cardapio_dia=cardapio
        ).select_related('receita', 'tipo_refeicao')
        
        # Verifica disponibilidade para cada item
        itens_preparados = []
        for item in itens:
            rendimento_padrao = item.receita.rendimento
            disponivel, info = verificar_disponibilidade_ingredientes(
                escola, item.receita, rendimento_padrao
            )
            
            itens_preparados.append({
                'item': item,
                'estoque_ok': disponivel,
                'porcoes_sugeridas': rendimento_padrao,
                'porcoes_maximas': self._calcular_maximo_porcoes(info) if not disponivel else rendimento_padrao,
                'faltantes': info.get('faltantes', []),
                'ingredientes': info['ingredientes']
            })
        
        ctx.update({
            'cardapio': cardapio,
            'itens': itens_preparados,
            'hoje': hoje,
            'total_itens': len(itens_preparados),
            'itens_com_estoque': sum(1 for i in itens_preparados if i['estoque_ok']),
        })
        
        return ctx
    
    def _calcular_maximo_porcoes(self, detalhes):
        """Calcula o máximo de porções possível com estoque atual"""
        min_ratio = float('inf')
        for ing in detalhes['ingredientes']:
            if ing['necessario'] > 0:
                ratio = ing['disponivel'] / ing['necessario']
                if ratio < min_ratio:
                    min_ratio = ratio
        return int(min_ratio) if min_ratio != float('inf') else 0
    
    def post(self, request, *args, **kwargs):
        """Processa o formulário de execução"""
        escola = self.get_escola_usuario()
        hoje = timezone.now().date()
        
        if not escola:
            messages.error(request, "Escola não encontrada.")
            return redirect('modulo_merendeiras:cardapio_hoje')
        
        # Coleta as porções personalizadas do formulário
        porcoes_override = {}
        for key, value in request.POST.items():
            if key.startswith('porcoes_'):
                receita_id = int(key.replace('porcoes_', ''))
                try:
                    porcoes_override[receita_id] = int(value)
                except ValueError:
                    porcoes_override[receita_id] = 0
        
        # Busca cardápio
        cardapio = self.get_cardapio_do_dia(escola, hoje)
        
        if not cardapio:
            messages.error(request, "Cardápio não encontrado.")
            return redirect('modulo_merendeiras:cardapio_hoje')
        
        try:
            with transaction.atomic():
                resultado = executar_cardapio_do_dia(
                    escola=escola,
                    data=hoje,
                    usuario=request.user,
                    cardapio_dia=cardapio,
                    porcoes_override=porcoes_override if porcoes_override else None
                )
                
                # Redireciona para página de resultado
                execucao_id = resultado['execucao_dia_id']
                
                if resultado['sucessos']:
                    msg = f"Cardápio executado com sucesso! {len(resultado['sucessos'])} receita(s) preparada(s)."
                    if resultado['falhas']:
                        msg += f" ({len(resultado['falhas'])} falha(s))"
                    messages.success(request, msg)
                else:
                    messages.error(request, "Não foi possível executar nenhuma receita. Verifique o estoque.")
                
                return redirect('modulo_merendeiras:execucao_detalhe', pk=execucao_id)
                
        except Exception as e:
            messages.error(request, f"Erro ao executar cardápio: {str(e)}")
            return redirect('modulo_merendeiras:cardapio_hoje')


class ExecucaoCardapioDetailView(BaseMerendeiraView, DetailView):
    """
    Mostra o resultado detalhado da execução do cardápio.
    """
    model = ExecucaoCardapioDia
    template_name = "modulo_merendeiras/cardapio/execucao_detalhe.html"
    context_object_name = 'execucao'
    
    def get_queryset(self):
        # Segurança: só vê execuções da sua escola
        escola = self.get_escola_usuario()
        return super().get_queryset().filter(escola=escola)
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        execucao = self.object
        
        itens = ExecucaoCardapioItem.objects.filter(
            execucao_cardapio=execucao
        ).select_related('receita', 'tipo_refeicao', 'execucao_receita')
        
        # Separa por status
        ctx.update({
            'itens_executados': itens.filter(status='EXECUTADO'),
            'itens_pendentes': itens.filter(status__in=['PENDENTE', 'FALTANDO_ESTOQUE']),
            'itens_cancelados': itens.filter(status='CANCELADO'),
            'pode_finalizar': execucao.status == 'EM_EXECUCAO',
            'pode_cancelar': execucao.status in ['EM_EXECUCAO', 'PLANEJADO'],
        })
        
        return ctx


class FinalizarExecucaoView(BaseMerendeiraView, View):
    """
    View para finalizar manualmente uma execução em andamento.
    """
    def post(self, request, pk):
        escola = self.get_escola_usuario()
        
        try:
            execucao = ExecucaoCardapioDia.objects.get(pk=pk, escola=escola)
            
            if execucao.status not in ['EM_EXECUCAO', 'PARCIAL']:
                messages.error(request, "Esta execução não pode ser finalizada.")
                return redirect('modulo_merendeiras:execucao_detalhe', pk=pk)
            
            # Atualiza quantidade de atendidos se informado
            quantidade_atendidos = request.POST.get('quantidade_atendidos')
            if quantidade_atendidos:
                execucao.quantidade_atendidos = int(quantidade_atendidos)
            
            execucao.status = 'EXECUTADO'
            execucao.finalizado_em = timezone.now()
            execucao.save()
            
            messages.success(request, "Execução finalizada com sucesso!")
            
        except ExecucaoCardapioDia.DoesNotExist:
            messages.error(request, "Execução não encontrada.")
        
        return redirect('modulo_merendeiras:execucao_detalhe', pk=pk)


class HistoricoExecucoesView(BaseMerendeiraView, ListView):
    """
    Histórico de execuções anteriores.
    """
    model = ExecucaoCardapioDia
    template_name = "modulo_merendeiras/cardapio/historico_execucoes.html"
    context_object_name = 'execucoes'
    paginate_by = 10
    
    def get_queryset(self):
        escola = self.get_escola_usuario()
        return ExecucaoCardapioDia.objects.filter(
            escola=escola
        ).select_related('cardapio_dia').order_by('-data')
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['hoje'] = timezone.now().date()
        return ctx


class CancelarReceitaView(BaseMerendeiraView, View):
    """
    Cancela uma receita específica dentro de uma execução.
    """
    def post(self, request, execucao_pk, item_pk):
        escola = self.get_escola_usuario()
        
        try:
            item = ExecucaoCardapioItem.objects.get(
                pk=item_pk,
                execucao_cardapio__pk=execucao_pk,
                execucao_cardapio__escola=escola
            )
            
            if item.status in ['EXECUTADO', 'CANCELADO']:
                messages.error(request, "Esta receita já foi processada.")
                return redirect('modulo_merendeiras:execucao_detalhe', pk=execucao_pk)
            
            motivo = request.POST.get('motivo', 'Cancelado pelo usuário')
            
            # Se tem execução de receita iniciada, cancela
            if item.execucao_receita:
                item.execucao_receita.cancelar(request.user, motivo)
            
            item.status = 'CANCELADO'
            item.motivo_falha = motivo
            item.save()
            
            # Verifica se precisa atualizar status geral
            execucao = item.execucao_cardapio
            itens_pendentes = execucao.itens_executados.exclude(status__in=['EXECUTADO', 'CANCELADO']).count()
            
            if itens_pendentes == 0:
                executados = execucao.itens_executados.filter(status='EXECUTADO').count()
                if executados == 0:
                    execucao.status = 'CANCELADO'
                else:
                    execucao.status = 'PARCIAL'
                execucao.save()
            
            messages.success(request, "Receita cancelada com sucesso.")
            
        except ExecucaoCardapioItem.DoesNotExist:
            messages.error(request, "Item não encontrado.")
        
        return redirect('modulo_merendeiras:execucao_detalhe', pk=execucao_pk)
