from django.views.generic import TemplateView
from django.db.models import Sum, F, Count, Q, Prefetch
from django.utils import timezone
from datetime import timedelta
from rh.models import Escola
from ...models import EstoqueEscola, MovimentacaoEstoque, Produto

class EstoqueEscolaDashboardView(TemplateView):
    template_name = "merendaEscolar/escola/estoque_escola_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        escola_id = self.kwargs.get("escola_id")
        self.escola = Escola.objects.get(pk=escola_id)
        
        hoje = timezone.now().date()
        alerta_dias = hoje + timedelta(days=7)
        
        # Busca otimizada com relacionamentos
        estoque_qs = EstoqueEscola.objects.filter(
            escola=self.escola
        ).select_related(
            'produto', 
            'produto__unidade_medida',
            'produto__categoria'
        ).order_by('data_validade')
        
        # Métricas detalhadas por produto
        produtos_analise = []
        total_valor_estimado = 0
        
        for item in estoque_qs:
            # Cálculos de saúde do estoque
            qtd_atual = float(item.quantidade)
            qtd_minimo = float(item.produto.estoque_minimo) if item.produto.estoque_minimo else 0
            
            # Percentual em relação ao mínimo (para barra visual)
            if qtd_minimo > 0:
                pct_sobrando = (qtd_atual / qtd_minimo) * 100
                ratio = min(200, max(0, pct_sobrando))
            else:
                pct_sobrando = 100 if qtd_atual > 0 else 0
                ratio = 100 if qtd_atual > 0 else 0
            
            # Análise de validade
            status_validade = "normal"
            dias_validade = None
            dias_vencidos_abs = 0  # NOVO: Valor absoluto para template
            classe_validade = "normal"
            
            if item.data_validade:
                dias_validade = (item.data_validade - hoje).days
                
                if dias_validade < 0:
                    status_validade = "vencido"
                    classe_validade = "vencido"
                    dias_vencidos_abs = abs(dias_validade)  # Cálculo no Python
                elif dias_validade <= 7:
                    status_validade = "critico"
                    classe_validade = "critico"
                elif dias_validade <= 30:
                    status_validade = "alerta"
                    classe_validade = "alerta"
            
            # Status geral do item (pior dos cenários)
            if classe_validade == "vencido" or (qtd_minimo > 0 and qtd_atual < qtd_minimo):
                status_geral = "critico"
            elif classe_validade == "critico" or (qtd_minimo > 0 and qtd_atual < qtd_minimo * 1.2):
                status_geral = "alerta"
            else:
                status_geral = "normal"
            
            produtos_analise.append({
                'id': item.id,
                'produto': item.produto,
                'quantidade': qtd_atual,
                'unidade': item.produto.unidade_medida.sigla if item.produto.unidade_medida else 'un',
                'minimo': qtd_minimo,
                'pct_minimo': ratio,
                'lote': item.lote,
                'validade': item.data_validade,
                'dias_validade': dias_validade,
                'dias_vencidos_abs': dias_vencidos_abs,  # NOVO: Passado para template
                'status_validade': status_validade,
                'classe_validade': classe_validade,
                'status_geral': status_geral,
                'categoria': item.produto.categoria.nome if item.produto.categoria else 'Sem categoria',
                'atualizado': item.atualizado_em,
            })
        
        # KPIs Reais (mantidos iguais...)
        total_itens_distintos = len(produtos_analise)
        total_unidades = sum(p['quantidade'] for p in produtos_analise)
        
        produtos_vencidos = sum(1 for p in produtos_analise if p['classe_validade'] == 'vencido')
        produtos_vencendo = sum(1 for p in produtos_analise if p['classe_validade'] == 'critico')
        produtos_alerta_val = sum(1 for p in produtos_analise if p['classe_validade'] == 'alerta')
        
        abaixo_minimo = sum(1 for p in produtos_analise if p['status_geral'] == 'critico' and p['pct_minimo'] < 100)
        
        # Última movimentação na escola
        ultima_mov = MovimentacaoEstoque.objects.filter(
            escola=self.escola
        ).order_by('-data_movimentacao').first()
        
        tempo_ultima_mov = None
        if ultima_mov:
            delta = timezone.now() - ultima_mov.data_movimentacao
            if delta.days > 0:
                tempo_ultima_mov = f"{delta.days} dia{'s' if delta.days > 1 else ''}"
            elif delta.seconds // 3600 > 0:
                tempo_ultima_mov = f"{delta.seconds // 3600}h"
            else:
                tempo_ultima_mov = "agora"
        
        context.update({
            "escola": self.escola,
            "produtos": produtos_analise,
            
            # KPIs
            "kpi_total_produtos": total_itens_distintos,
            "kpi_total_unidades": int(total_unidades),
            "kpi_vencidos": produtos_vencidos,
            "kpi_vencendo_7d": produtos_vencendo,
            "kpi_abaixo_minimo": abaixo_minimo,
            "kpi_ultima_movimentacao": tempo_ultima_mov,
            
            "filtros": {
                'vencidos': produtos_vencidos,
                'criticos': produtos_vencendo + produtos_vencidos + abaixo_minimo,
                'regulares': total_itens_distintos - (produtos_vencidos + produtos_vencendo + abaixo_minimo)
            }
        })

        return context
