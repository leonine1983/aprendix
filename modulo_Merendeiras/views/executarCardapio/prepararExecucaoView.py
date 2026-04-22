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
    
    # Analisa a quantidade de alunos disponivel no modulo gestão_escolar
    def _get_quantidade_alunos_por_turno(self, escola, hoje):
        """
        Busca a quantidade de alunos matriculados por turno para a escola.
        Retorna um dict com totais por turno e o total geral,
        ou None se não houver matrículas cadastradas.
        
        Tenta importar do gestao_escolar. Se o app não estiver disponível,
        retorna None silenciosamente para que a merendeira informe manualmente.
        """
        try:
            from gestao_escolar.models import Matriculas

            # Alunos ativos por turno (exclui desistentes, transferidos, etc.)
            matriculas = Matriculas.objects.filter(
                turma__escola=escola,
                turma__ano_letivo__ativo=True,  # ajuste o campo conforme seu AnoLetivo
                desistente=False,
                transferido=False,
            ).select_related('turma')

            if not matriculas.exists():
                return None

            # Agrupa por turno
            from django.db.models import Count
            por_turno = (
                matriculas
                .values('turma__turno')
                .annotate(total=Count('id'))
                .order_by('turma__turno')
            )

            turnos = {item['turma__turno']: item['total'] for item in por_turno}
            total = sum(turnos.values())

            return {
                'por_turno': turnos,
                'total': total,
                'fonte': 'matriculas',  # indica que veio do sistema
            }

        except Exception:
            # App gestao_escolar não instalado ou erro inesperado
            return None

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
            dia=cardapio_dia
        ).select_related('receita', 'tipo_refeicao')
        
        # Verifica disponibilidade para cada item
        itens_preparados = []
        for item in itens:
            # CORREÇÃO: Usar rendimento padrão 100 se não existir
            rendimento_padrao = getattr(item.receita, 'rendimento', 100)
            
            # Verifica disponibilidade para o rendimento padrão (100 porções)
            disponivel, info = verificar_disponibilidade_ingredientes(
                escola, item.receita, rendimento_padrao
            )
            
            # CALCULA O MÁXIMO REAL baseado no estoque disponível
            # Agora calculamos SEMPRE, não apenas quando não está disponível
            maximo_calculado = self._calcular_maximo_porcoes(info, rendimento_padrao)
            
            # Se o cálculo retornar 0 mas tiver estoque, usa o rendimento padrão ou 1000
            if maximo_calculado == 0 and disponivel:
                maximo_calculado = 1000  # Ou um número alto suficiente
            
            itens_preparados.append({
                'item': item,
                'estoque_ok': disponivel,
                'porcoes_sugeridas': rendimento_padrao,
                'porcoes_maximas': maximo_calculado,  # AGORA SEMPRE TEM O VALOR REAL DO ESTOQUE
                'faltantes': info.get('faltantes', []),
                'ingredientes': info['ingredientes']
            })
        
        # ── NOVO: Quantidade de alunos ──────────────────────────────
        dados_alunos = self._get_quantidade_alunos_por_turno(escola, hoje)
        
        ctx.update({
            'cardapio': cardapio_dia,
            'itens': itens_preparados,
            'hoje': hoje,
            'total_itens': len(itens_preparados),
            'itens_com_estoque': sum(1 for i in itens_preparados if i['estoque_ok']),
            # Novos campos:
            'quantidade_alunos': dados_alunos['total'] if dados_alunos else None,
            'alunos_por_turno': dados_alunos['por_turno'] if dados_alunos else None,
            'alunos_fonte_matriculas': dados_alunos is not None,  # True = veio do sistema
        })

        return ctx
    
    def _calcular_maximo_porcoes(self, detalhes, rendimento_base=100):
        """
        Calcula o máximo de porções possível com estoque atual.
        
        O 'detalhes' contém os ingredientes calculados para 'rendimento_base' porções.
        Portanto, se temos estoque para X vezes o necessário para 100 porções,
        podemos fazer X * 100 porções.
        """
        if not detalhes or not detalhes.get('ingredientes'):
            return rendimento_base  # Retorna o padrão se não houver dados
        
        min_ratio = float('inf')
        
        for ing in detalhes['ingredientes']:
            necessario = ing.get('necessario', 0)
            disponivel = ing.get('disponivel', 0)
            
            # Evita divisão por zero
            if necessario > 0:
                # Ratio = quantas vezes cabe o necessário no disponível
                ratio = disponivel / necessario
                if ratio < min_ratio:
                    min_ratio = ratio
        
        # Se min_ratio for infinito (não entrou no loop ou sem ingredientes), retorna padrão
        if min_ratio == float('inf'):
            return rendimento_base
        
        # Multiplica pelo rendimento base (pois o necessário é para 'rendimento_base' porções)
        max_porcoes = int(min_ratio * rendimento_base)
        
        # Limita a 1000 (máximo do sistema) ou retorna o valor real
        return min(max_porcoes, 1000)
    
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
        
        # ── NOVO: Captura quantidade informada manualmente (se não veio de matrículas)
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
                    porcoes_override=porcoes_override if porcoes_override else None,
                    quantidade_alunos=quantidade_alunos_manual,  # repasse para o serviço se quiser salvar
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
