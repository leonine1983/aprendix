# utils.py
import plotly.express as px
import plotly.io as pio
from rh.models import Escola, Decreto  # Ajuste conforme necessário

# utils.py
from rh.models import Escola, Decreto, Ano

def processar_dados(request, ano, escola_id):
    # buscar objeto do ano letivo
    ano_obj = Ano.objects.get(id=ano)

    # salvar ano letivo na sessão
    request.session['anoLetivo_id'] = ano_obj.id
    request.session['anoLetivo_nome'] = ano_obj.ano

    # valores padrão caso não haja matriculas
    matriculas_all = []
    totais_vagas_disponiveis_total = {
        'total_autistas': 0,
        'total_masculino': 0,
        'total_feminino': 0,
        'total_brancos': 0,
        'total_pardos': 0,
        'total_negros': 0,
        'total_amarelos': 0,
        'total_indigena': 0,
        'total_nDeclarados': 0,
        'total_p': 0,
        'total_pp': 0,
        'total_m': 0,
        'total_g': 0,
        'gg': 0,
        'total_turmas': 0,
        'total_vagas': 0,
        'total_matriculas': 0,
        'vagas_disponiveis_total': 0,
    }

    # pegar matriculas da sessão
    matriculas = request.session.get('matriculas_painel')
    if matriculas is not None:
        matriculas_painel = matriculas.filter(ano_letivo=ano.id)
        turmas_info = []

        totais = totais_vagas_disponiveis_total.copy()  # copiar valores zerados para iniciar cálculos

        for turma in matriculas_painel:
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

            # atualiza totais
            totais['total_autistas'] += alunosEspecroAutistas
            totais['total_masculino'] += alunosMasculino
            totais['total_feminino'] += alunosFeminino
            totais['total_brancos'] += alunosBrancos
            totais['total_pardos'] += alunosPardos
            totais['total_negros'] += alunosNegros
            totais['total_amarelos'] += alunosAmarela
            totais['total_indigena'] += alunosIndigena
            totais['total_nDeclarados'] += alunosN_declarado
            totais['total_pp'] += alunosUniformePP
            totais['total_p'] += alunosUniformeP
            totais['total_m'] += alunosUniformeM
            totais['total_g'] += alunosUniformeG
            totais['gg'] += alunosUniformeGG
            totais['total_turmas'] += 1
            totais['total_vagas'] += turma.quantidade_vagas
            totais['total_matriculas'] += turma.related_matricula_turma.count()

            # adiciona info da turma
            turmas_info.append({
                'nome': turma.nome,
                'descritivo_turma': turma.descritivo_turma,
                'matriculas': turma.related_matricula_turma.count(),
                'quantidade_vagas': turma.quantidade_vagas,
                'vagas_disponiveis': turma.vagas_disponiveis if turma.vagas_disponiveis else turma.quantidade_vagas,
                'autistas': alunosEspecroAutistas,
                'masculino': alunosMasculino,
                'feminino': alunosFeminino,
                'brancos': alunosBrancos,
                'pardos': alunosPardos,
                'negros': alunosNegros,
                'amarelos': alunosAmarela,
                'indigenas': alunosIndigena,
                'nDeclarados': alunosN_declarado,
                'alunosPP': alunosUniformePP,
                'alunosP': alunosUniformeP,
                'alunosM': alunosUniformeM,
                'alunosG': alunosUniformeG,
                'alunosGG': alunosUniformeGG
            })

        # calcular vagas disponíveis
        totais['vagas_disponiveis_total'] = totais['total_vagas'] - totais['total_matriculas']

        # salvar dados finais
        matriculas_all = turmas_info
        totais_vagas_disponiveis_total = totais

    # devolver para a view
    return {
        "matriculas_all": matriculas_all,
        "totais_vagas_disponiveis_total": totais_vagas_disponiveis_total
    }
