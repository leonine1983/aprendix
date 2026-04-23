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



class ExecucaoCardapioDetailView(BaseMerendeiraView, DetailView):
    """
    Mostra o resultado detalhado da execução do cardápio.
    """
    model = ExecucaoCardapioDia
    template_name = "modulo_merendeiras/cadapioHoje/execucao_detalhe.html"
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

        itens_executados = itens.filter(status='EXECUTADO')
        itens_pendentes = itens.filter(status__in=['PENDENTE', 'FALTANDO_ESTOQUE'])
        itens_cancelados = itens.filter(status='CANCELADO')

        total_itens = itens.count()

        ctx.update({
            'itens_executados': itens_executados,
            'itens_pendentes': itens_pendentes,
            'itens_cancelados': itens_cancelados,
            'total_itens': total_itens,
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
