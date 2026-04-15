from django.views.generic import ListView
from django.db.models import Max, Prefetch
from django.utils import timezone
from datetime import timedelta
from rh.models import Escola
from merendaEscolar.models import EstoqueEscola, MovimentacaoEstoque

class ListaEscolasView(ListView):
    model = Escola
    template_name = "merendaEscolar/escola/escolas_list.html"
    context_object_name = "escolas"
    ordering = ["nome_escola"]
    paginate_by = 12

    def get_queryset(self):
        qs = super().get_queryset()
        self.termo_busca = self.request.GET.get("q", "")
        
        if self.termo_busca:
            qs = qs.filter(nome_escola__icontains=self.termo_busca)
        
        # Otimização: prefetch do estoque com produtos para evitar N+1
        qs = qs.prefetch_related(
            Prefetch(
                'estoque_escola',
                queryset=EstoqueEscola.objects.select_related('produto')
            )
        )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["termo_busca"] = self.termo_busca
        
        hoje = timezone.now().date()
        data_limite_alerta = hoje + timedelta(days=7)
        
        # Bulk fetch das últimas movimentações por escola (eficiente)
        escolas_ids = [e.id for e in context['page_obj']]
        ultimas_movs = {}
        
        for mov in MovimentacaoEstoque.objects.filter(
            escola_id__in=escolas_ids
        ).values('escola_id').annotate(ultima=Max('data_movimentacao')):
            ultimas_movs[mov['escola_id']] = mov['ultima']
        
        # Calcular métricas para cada escola
        escolas_com_metricas = []
        total_abaixo_minimo = 0
        
        for escola in context['page_obj']:
            estoque_list = list(escola.estoque_escola.all())
            
            # Métricas calculadas
            total_itens = sum(e.quantidade for e in estoque_list)
            total_produtos = len(estoque_list)
            
            # Análise de validade e estoque mínimo
            vencidos = sum(1 for e in estoque_list 
                          if e.data_validade and e.data_validade < hoje)
            criticos = sum(1 for e in estoque_list 
                           if e.data_validade and hoje <= e.data_validade <= data_limite_alerta)
            abaixo_minimo = sum(1 for e in estoque_list 
                               if e.quantidade < e.produto.estoque_minimo)
            
            total_abaixo_minimo += abaixo_minimo
            
            # Status dinâmico baseado em regras de negócio reais
            if vencidos > 0 or abaixo_minimo > 0:
                status_class = 'critico'
                status_label = 'Crítico'
                status_desc = f'{abaixo_minimo} abaixo do mín' if abaixo_minimo > 0 else 'vencidos'
            elif criticos > 0:
                status_class = 'alerta'
                status_label = 'Alerta'
                status_desc = f'{criticos} próx. venc.'
            else:
                status_class = 'normal'
                status_label = 'Normal'
                status_desc = 'Estoque OK'
            
            # Cálculo da "Ocupação" (Saúde do Estoque)
            # 100% = ideal (acima do mínimo e sem vencimentos próximos)
            if estoque_list:
                soma_minimos = sum(e.produto.estoque_minimo for e in estoque_list)
                if soma_minimos > 0:
                    # Razão entre estoque atual e (mínimo * 1.5)
                    razao = total_itens / (soma_minimos * 1.5)
                    ocupacao = min(100, int(razao * 100))
                else:
                    ocupacao = 100
                
                # Penalidades reais
                if vencidos > 0:
                    ocupacao = max(0, ocupacao - (vencidos * 15))
                if abaixo_minimo > 0:
                    ocupacao = max(0, ocupacao - (abaixo_minimo * 10))
            else:
                ocupacao = 0
            
            # Tempo relativo da última atualização
            ultima = ultimas_movs.get(escola.id)
            if ultima:
                delta = timezone.now() - ultima
                if delta.days > 0:
                    tempo_str = f"há {delta.days} dia{'s' if delta.days > 1 else ''}"
                elif delta.seconds // 3600 > 0:
                    horas = delta.seconds // 3600
                    tempo_str = f"há {horas} hora{'s' if horas > 1 else ''}"
                elif delta.seconds // 60 > 0:
                    mins = delta.seconds // 60
                    tempo_str = f"há {mins} min"
                else:
                    tempo_str = "agora"
            else:
                tempo_str = "nunca atualizado"
            
            escolas_com_metricas.append({
                'escola': escola,
                'total_itens': int(total_itens),
                'total_produtos': total_produtos,
                'ultima_atualizacao': tempo_str,
                'status_class': status_class,
                'status_label': status_label,
                'status_desc': status_desc,
                'ocupacao': ocupacao,
                'vencidos': vencidos,
                'criticos': criticos,
                'abaixo_minimo': abaixo_minimo,
                'cor_progresso': self._get_cor_progresso(ocupacao, status_class),
            })
        
        context['escolas_metricas'] = escolas_com_metricas
        
        # KPIs reais globais
        context['kpi_escolas_criticas'] = sum(1 for e in escolas_com_metricas if e['status_class'] == 'critico')
        context['kpi_escolas_alerta'] = sum(1 for e in escolas_com_metricas if e['status_class'] == 'alerta')
        context['kpi_itens_abaixo_minimo'] = total_abaixo_minimo
        
        return context
    
    def _get_cor_progresso(self, ocupacao, status):
        """Retorna cor do gradiente baseada na saúde do estoque"""
        if status == 'critico':
            return '#ef4444'  # vermelho
        elif status == 'alerta':
            return '#f59e0b'  # amarelo
        return '#10b981' if ocupacao >= 80 else '#3b82f6'  # verde ou azul
