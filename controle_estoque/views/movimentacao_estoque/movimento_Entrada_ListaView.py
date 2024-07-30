from controle_estoque.models import Movimentacao_Estoque, Alimentos
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.views.generic import ListView
import django_filters
# Lib pra criação de graficos
import plotly.graph_objects as go
import pandas as pd





class Meu_filtro(django_filters.FilterSet):
    class Meta:
        model = Movimentacao_Estoque
        fields = {
            'tipo':['exact']
        }


class MovimentoEstoque_ListView(ListView):
    model = Movimentacao_Estoque
    template_name = 'controle_estoque/movimentacao_estoque/movi_lista.html'
    paginate_by = 10    
    filterset_class = Meu_filtro

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(tipo='entrada')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        alimentos_estoque = Alimentos.objects.all()
        alimentos_saida = Movimentacao_Estoque.objects.filter(tipo='saida')[:10]
        produto = []
        quantidade = []
        for ali in alimentos_estoque:
            produto.append(ali.nome)
            quantidade.append(int(ali.quantidade_disponivel)/100)
        data = {
            'x': produto,
            'y': quantidade
        }
        df = pd.DataFrame(data)

        colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FFA500']  # Lista de cores hexadecimais

        fig = go.Figure(data=go.Bar(x=df['x'], y=df['y'], marker=dict(color=colors)))
        fig.update_layout(width=1000)
        plot_div = fig.to_html(full_html=True, config={'displayModeBar': True})

        context["title_geral"] = 'Depósito Geral'
        context['svgE'] = mark_safe('<svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 640 512"><!--! Font Awesome Free 6.4.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M208 96a48 48 0 1 0 0-96 48 48 0 1 0 0 96zM123.7 200.5c1-.4 1.9-.8 2.9-1.2l-16.9 63.5c-5.6 21.1-.1 43.6 14.7 59.7l70.7 77.1 22 88.1c4.3 17.1 21.7 27.6 38.8 23.3s27.6-21.7 23.3-38.8l-23-92.1c-1.9-7.8-5.8-14.9-11.2-20.8l-49.5-54 19.3-65.5 9.6 23c4.4 10.6 12.5 19.3 22.8 24.5l26.7 13.3c15.8 7.9 35 1.5 42.9-14.3s1.5-35-14.3-42.9L281 232.7l-15.3-36.8C248.5 154.8 208.3 128 163.7 128c-22.8 0-45.3 4.8-66.1 14l-8 3.5c-32.9 14.6-58.1 42.4-69.4 76.5l-2.6 7.8c-5.6 16.8 3.5 34.9 20.2 40.5s34.9-3.5 40.5-20.2l2.6-7.8c5.7-17.1 18.3-30.9 34.7-38.2l8-3.5zm-30 135.1L68.7 398 9.4 457.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L116.3 441c4.6-4.6 8.2-10.1 10.6-16.1l14.5-36.2-40.7-44.4c-2.5-2.7-4.8-5.6-7-8.6zM550.6 153.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L530.7 224H384c-17.7 0-32 14.3-32 32s14.3 32 32 32H530.7l-25.4 25.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0l80-80c12.5-12.5 12.5-32.8 0-45.3l-80-80z"/></svg>')
        context["title"] = ' Movimento de Entrada'
        context['class_active'] = 'Deposito Central'
        context['active'] = 'Deposito Central'
        context['fornecedor'] = 'cadastro'
        context['alimentos_estoque'] = alimentos_estoque
        context['alimentos_saida'] = alimentos_saida
        context['plot_div'] = plot_div

        return context

        """          
        pio.templates["custom"].layout.width = 200
pio.templates["custom"].layout.height = 200   
        import plotly.graph_objs as go
from django.http import HttpResponse
from django.shortcuts import render

def plotly_view(request):
    data = [
        go.Scatter(
            x=[1, 2, 3, 4, 5],
            y=[1, 3, 2, 5, 4],
            mode='lines',
            name='example'
        )
    ]
    layout = go.Layout(
        title='Plotly Example',
        xaxis=dict(title='X-axis'),
        yaxis=dict(title='Y-axis')
    )
    fig = go.Figure(data=data, layout=layout)
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return render(request, 'plotly_app/plotly_view.html', {'plot_div': plot_div})

        
        
        
        
        
        
        
        
        """