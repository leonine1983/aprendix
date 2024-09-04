from gestao_escolar.models import *
from django.shortcuts import redirect
from django.urls import reverse
from gestao_escolar.models import AnoLetivo
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import plotly.express as px
import plotly.io as pio


@login_required
def seleciona_anoLetivo_session(request, pk):
    ano = AnoLetivo.objects.get(id=pk)  # Obtendo o objeto AnoLetivo pelo ID
    print(f'ano é {ano}')
    if ano:
        request.session['anoLetivo_id'] = ano.id    
        request.session['anoLetivo_nome'] = str(ano.ano) 
        matriculas = request.session['matriculas_painel'] 
        matriculas_painel = matriculas.filter (ano_letivo = ano.id)
        request.session['matriculas_all'] = matriculas_painel

        # cria os graficos
        fig = px.bar(x=["a", "b", "c"], y=[1, 3, 2])
        graph_json = pio.to_json(fig)
        request.session['matriculas_graficos'] =graph_json
        


    
    ano = request.session.get('anoLetivo_nome', 'Ano letivo não definido')
    messages.success(request, f"Ano letivo selecionado: {ano}")


    return redirect(reverse('Gestao_Escolar:GE_Escola_inicio'))
