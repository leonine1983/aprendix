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
        
        turmas_info = []  # Lista para armazenar informações das turmas
        total_autistas = 0
        total_turmas = 0
        total_vagas = 0
        total_matriculas = 0

        for turma in matriculas_painel:
            # Contagem de alunos com espectro autista para cada turma
            alunosEspecroAutistas = turma.related_matricula_turma.filter(aluno__espectro_autista=True).count()

            # Atualiza os totais
            total_autistas += alunosEspecroAutistas
            total_turmas += 1
            total_vagas += turma.quantidade_vagas
            total_matriculas += turma.related_matricula_turma.all().count()

            # Informações da turma, incluindo o número de autistas
            turmas_info.append({
                'nome': turma.nome,
                'descritivo_turma': turma.descritivo_turma,
                'matriculas': turma.related_matricula_turma.all().count(),
                'quantidade_vagas': turma.quantidade_vagas,
                'vagas_disponiveis': turma.vagas_disponiveis if turma.vagas_disponiveis else turma.quantidade_vagas,
                'autistas': alunosEspecroAutistas
            })
        
        # Armazenando as informações das turmas e alunos autistas na sessão
        request.session['matriculas_all'] = turmas_info
        
        # Calcular vagas disponíveis
        vagas_disponiveis_total = total_vagas - total_matriculas

        # Armazenando os totais para exibição na tabela
        request.session['totais'] = {
            'total_autistas': total_autistas,
            'total_turmas': total_turmas,
            'total_vagas': total_vagas,
            'total_matriculas': total_matriculas,
            'vagas_disponiveis_total': vagas_disponiveis_total  # Armazenando as vagas disponíveis
        }
    
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
