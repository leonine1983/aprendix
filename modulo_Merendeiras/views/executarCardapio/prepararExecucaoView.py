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

from modulo_Merendeiras.models import (
    ExecucaoCardapioDia,
    # services
    executar_cardapio_do_dia,
    verificar_disponibilidade_ingredientes
)
class PrepararExecucaoView(BaseMerendeiraView, TemplateView):
    template_name = "modulo_merendeiras/cadapioHoje/preparar_execucao.html"
    
    def get_cardapio_do_dia(self, escola, hoje):
        """Busca cardápio ativo da escola e retorna o dia específico"""
        dia_semana = hoje.isoweekday()
        
        # Sábado (6) e Domingo (7) não têm cardápio
        if dia_semana > 5:
            return None
        
        # 1. Busca o cardápio ativo vigente para a escola
        cardapio = Cardapio.objects.filter(
            cardapioescola__escola=escola,
            ativo=True,
            data_inicio__lte=hoje,
            data_fim__gte=hoje
        ).first()
        
        if not cardapio:
            return None
        
        # 2. Calcula qual semana estamos dentro do período do cardápio
        dias_desde_inicio = (hoje - cardapio.data_inicio).days
        numero_semana = (dias_desde_inicio // 7) + 1
        
        # 3. Busca a semana específica
        total_semanas = CardapioSemana.objects.filter(cardapio=cardapio).count()
        if numero_semana > total_semanas:
            return None  # Fora do período do cardápio
        
        semana = CardapioSemana.objects.filter(
            cardapio=cardapio,
            numero=numero_semana
        ).first()
        
        if not semana:
            return None
        
        # 4. Retorna o dia da semana específico
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
        
        # Busca o dia do cardápio (CardapioDia)
        cardapio_dia = self.get_cardapio_do_dia(escola, hoje)
        
        if not cardapio_dia:
            messages.error(self.request, "Não há cardápio planejado para hoje.")
            return redirect('modulo_merendeiras:cardapio_hoje')
        
        # CORREÇÃO: Usar campo 'dia' ao invés de 'cardapio_dia'
        itens = CardapioItem.objects.filter(
            dia=cardapio_dia  # <-- CAMPO CORRETO
        ).select_related('receita', 'tipo_refeicao')
        
        # Verifica disponibilidade para cada item
        itens_preparados = []
        for item in itens:
            # CORREÇÃO: Usar rendimento padrão 100 se não existir
            rendimento_padrao = getattr(item.receita, 'rendimento', 100)
            
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
            'cardapio': cardapio_dia,
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
        escola = self.get_escola_usuario()
        hoje = timezone.now().date()
        
        if not escola:
            messages.error(request, "Escola não encontrada.")
            return redirect('modulo_merendeiras:cardapio_hoje')
        
        porcoes_override = {}
        for key, value in request.POST.items():
            if key.startswith('porcoes_'):
                receita_id = int(key.replace('porcoes_', ''))
                try:
                    porcoes_override[receita_id] = int(value)
                except ValueError:
                    porcoes_override[receita_id] = 0
        
        cardapio_dia = self.get_cardapio_do_dia(escola, hoje)
        
        if not cardapio_dia:
            messages.error(request, "Cardápio não encontrado.")
            return redirect('modulo_merendeiras:cardapio_hoje')
        
        try:
            with transaction.atomic():
                resultado = executar_cardapio_do_dia(
                    escola=escola,
                    data=hoje,
                    usuario=request.user,
                    cardapio_dia=cardapio_dia,
                    porcoes_override=porcoes_override if porcoes_override else None
                )
                
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
