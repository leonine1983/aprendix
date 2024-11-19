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

        total_masculino = 0
        total_feminino = 0

        total_brancos = 0
        total_pardos = 0
        total_negros = 0
        total_amarelos = 0
        total_indigena = 0
        total_nDeclarados = 0

        total_P = 0
        total_PP = 0
        total_M = 0
        total_G = 0
        total_GG = 0

        total_turmas = 0
        total_vagas = 0
        total_matriculas = 0

        for turma in matriculas_painel:
            # Contagem de alunos com espectro autista para cada turma
            alunosEspecroAutistas = turma.related_matricula_turma.filter(aluno__espectro_autista=True).count()
            alunosMasculino = turma.related_matricula_turma.filter(aluno__sexo__nome='Masculino').count()
            alunosFeminino = turma.related_matricula_turma.filter(aluno__sexo__nome='Feminino').count()

            alunosBrancos = turma.related_matricula_turma.filter(aluno__etnia__nome='Branca').count()            
            alunosPardos = turma.related_matricula_turma.filter(aluno__etnia__nome='Parda').count()
            alunosNegros = turma.related_matricula_turma.filter(aluno__etnia__nome='Negra').count()
            alunosAmarela = turma.related_matricula_turma.filter(aluno__etnia__nome='Amarela').count()
            alunosIndigena = turma.related_matricula_turma.filter(aluno__etnia__nome='Indigena').count()
            alunosN_declarado = turma.related_matricula_turma.filter(aluno__etnia__nome='Não declarado').count()

            alunosUniformePP = turma.related_matricula_turma.filter(camisa_tamanho__nome='PP').count()
            alunosUniformeP = turma.related_matricula_turma.filter(camisa_tamanho__nome='P').count()
            alunosUniformeM = turma.related_matricula_turma.filter(camisa_tamanho__nome='M').count()
            alunosUniformeG = turma.related_matricula_turma.filter(camisa_tamanho__nome='G').count()
            alunosUniformeGG = turma.related_matricula_turma.filter(camisa_tamanho__nome='GG').count()
            
            # Atualiza os totais            
            total_autistas += alunosEspecroAutistas
            # genero --------------------------------
            total_masculino += alunosMasculino
            total_feminino += alunosFeminino
            # etnia ---------------------------------
            total_brancos += alunosBrancos
            total_pardos += alunosPardos
            total_negros += alunosNegros
            total_amarelos += alunosAmarela
            total_indigena += alunosIndigena
            total_nDeclarados += alunosN_declarado
            # uniformes
            total_PP += alunosUniformePP
            total_P += alunosUniformeP
            total_M += alunosUniformeM
            total_G += alunosUniformeG
            total_GG += alunosUniformeGG


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
                'autistas': alunosEspecroAutistas,
                'masculino': alunosMasculino,
                'feminino': alunosFeminino,
                # Por etnia
                'brancos': alunosBrancos,
                'pardos': alunosPardos,
                'negros': alunosNegros,
                'amarelos': alunosAmarela,
                'indigenas': alunosIndigena,
                'nDeclarados': alunosN_declarado,
                # uniformes
                'alunosPP':alunosUniformePP,
                'alunosP':alunosUniformeP,
                'alunosM':alunosUniformeM,
                'alunosG':alunosUniformeG,
                'alunosGG':alunosUniformeGG
            })
        
        # Armazenando as informações das turmas e alunos autistas na sessão
        request.session['matriculas_all'] = turmas_info
        
        # Calcular vagas disponíveis
        vagas_disponiveis_total = total_vagas - total_matriculas

        # Armazenando os totais para exibição na tabela
        request.session['totais'] = {
            'total_autistas': total_autistas,
            # total genero -----------------
            'total_masculino': total_masculino,
            'total_feminino':total_feminino,
            # total etnia ------------------
            'total_brancos': total_brancos,
            'total_pardos' : total_pardos,
            'total_negros' : total_negros,
            'total_amarelos': total_amarelos,
            'total_indigenas': total_indigena,
            'total_nDeclarados': total_nDeclarados,
            'total_turmas': total_turmas,
            'total_vagas': total_vagas,
            'total_matriculas': total_matriculas,
            'vagas_disponiveis_total': vagas_disponiveis_total,  # Armazenando as vagas disponíveis,
            # Por uniforme
            'total_p': total_P,
            'total_pp': total_PP,
            'total_m': total_M,
            'total_g': total_G,
            'gg': total_GG,
        }
    
    # Cria os gráficos
    fig = px.bar(x=["a", "b", "c"], y=[1, 3, 2])
    graph_json = pio.to_json(fig)
    request.session['matriculas_graficos'] = graph_json

    # Decretos / Gestores
    local_destino = Escola.objects.get(id=escola_id)
    
    diretor = Decreto.objects.filter(destino=local_destino, profissao__nome_profissao="Diretor Escolar", Decreto_decretoAtivo__ano_ativo__id=ano.id).last()
    
    vice_diretor = Decreto.objects.filter(destino=local_destino, profissao__nome_profissao='Vice-Diretor Escolar', Decreto_decretoAtivo__ano_ativo__id=ano.id).last()
    coordenador = Decreto.objects.filter(destino=local_destino, profissao__nome_profissao='Coordenador Escolar', Decreto_decretoAtivo__ano_ativo__id=ano.id).last()
    secretario = Decreto.objects.filter(destino=local_destino, profissao__nome_profissao='Secretária escolar', Decreto_decretoAtivo__ano_ativo__id=ano.id).last()
    
    request.session['diretor'] = diretor
    request.session['vice_diretor'] = vice_diretor
    request.session['coordenador'] = coordenador
    request.session['secretario'] = secretario
