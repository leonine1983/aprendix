"""

from gestao_escolar.models import GestaoTurmas, Trimestre, TurmaDisciplina
from django.shortcuts import render

def boletim_trimestral(request, aluno_id, turma_id):
    # Obtém todas as turmas e disciplinas associadas ao aluno na turma específica
    aluno_boletim = GestaoTurmas.objects.filter(aluno__id=aluno_id, grade__turma__id=turma_id).select_related('grade__disciplina')
    trimestres = Trimestre.objects.filter(ano_letivo__turma__id=turma_id).order_by('id')  # Obtém os trimestres da turma
    grade = TurmaDisciplina.objects.filter(turma=turma_id)

    # Estrutura para armazenar as notas por disciplina em cada trimestre
    boletim = {}

    for disciplina in grade:
        boletim[disciplina.disciplina.nome] = {}
        for trimestre in trimestres:
            # Busca as notas do aluno para a disciplina no trimestre atual
            nota = aluno_boletim.filter(trimestre=trimestre, grade=disciplina).first()
            boletim[disciplina.disciplina.nome][trimestre.numero_nome] = {
                'nota': nota.notas if nota else None,
                'faltas': nota.faltas if nota else None,
                'parecer_descritivo': nota.parecer_descritivo if nota else None
            }

    context = {
        'conteudo_page': "boletim_trimestral",
        'boletim': boletim,
        'trimestres': trimestres,
        'grade': grade
    }
    return render(request, 'Escola/inicio.html', context)
"""



from gestao_escolar.models import  GestaoTurmas, Trimestre, TurmaDisciplina
from django.shortcuts import render

def boletim_trimestral(request, aluno_id, turma_id):
    aluno_boletim = GestaoTurmas.objects.filter(aluno = aluno_id)
    trimestres = Trimestre.objects.all()
    grade = TurmaDisciplina.objects.filter(turma = turma_id)

    context = {
        'conteudo_page':"boletim_trimestral",
        'aluno_boletim' : aluno_boletim,
        'trimestres': trimestres,
        'grade' : grade
    }
    return render(request, 'Escola/inicio.html', context)

