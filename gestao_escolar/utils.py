# utils.py
import plotly.express as px
import plotly.io as pio
from rh.models import Escola, Decreto  # Ajuste conforme necessário

def processar_dados(request, ano, escola_id):
    # Configurações de sessão
    request.session['anoLetivo_id'] = ano.id
    request.session['anoLetivo_nome'] = str(ano.ano)
    
    matriculas = request.session.get('matriculas_painel')
    if matriculas is not None:
        matriculas_painel = matriculas.filter(ano_letivo=ano.id)
        request.session['matriculas_all'] = matriculas_painel
    
    # Cria os gráficos
    fig = px.bar(x=["a", "b", "c"], y=[1, 3, 2])
    graph_json = pio.to_json(fig)
    request.session['matriculas_graficos'] = graph_json

    # Decretos / Gestores
    local_destino = Escola.objects.get(id=escola_id)
    
    diretor = Decreto.objects.filter(destino=local_destino, profissao__nome_profissao="Diretor Escolar", Decreto_decretoAtivo__ano_ativo__id=ano.id).last()
    print(f'o diretor é : {diretor}')
    
    vice_diretor = Decreto.objects.filter(destino=local_destino, profissao__nome_profissao='Vice-Diretor Escolar', Decreto_decretoAtivo__ano_ativo__id=ano.id).last()
    coordenador = Decreto.objects.filter(destino=local_destino, profissao__nome_profissao='Coordenador Escolar', Decreto_decretoAtivo__ano_ativo__id=ano.id).last()
    secretario = Decreto.objects.filter(destino=local_destino, profissao__nome_profissao='Secretária escolar', Decreto_decretoAtivo__ano_ativo__id=ano.id).last()
    
    request.session['diretor'] = diretor
    request.session['vice_diretor'] = vice_diretor
    request.session['coordenador'] = coordenador
    request.session['secretario'] = secretario
