from gestao_escolar.models import Turmas, Matriculas, GestaoTurmas, TurmaDisciplina
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required


@login_required
def listaTurmaApuracao (request):
    escola = request.session['escola_id']
    ano = request.session['anoLetivo_id']
    turma = Turmas.objects.filter(escola__id = escola, ano_letivo__id = ano)

    return render(request,'Escola/inicio.html' ,{
        'turma': turma,
        'conteudo_page': 'SelecinaTurmaApuração',
        'title_page': 'APURAÇÃO FINAL: Selecione um turma'
    })


@login_required
def selecionaTurmaSelecionada(request, turma_id):

    matriculas = Matriculas.objects.filter(turma__id=turma_id)
    gestao = GestaoTurmas.objects.filter(grade__turma__id=turma_id, trimestre__final=True).select_related('aluno', 'grade', 'grade__disciplina')

    disciplinas = TurmaDisciplina.objects.filter(turma__id=turma_id).select_related('disciplina').distinct()

    # Mapeamento: matricula_id -> disciplina_id -> {'media': x, 'faltas': y}
    dados_por_matricula = {}

    for g in gestao:
        matricula_id = g.aluno.id
        disciplina_id = g.grade.disciplina.id

        if matricula_id not in dados_por_matricula:
            dados_por_matricula[matricula_id] = {}

        dados_por_matricula[matricula_id][disciplina_id] = {
            'media': g.media_final,
            'faltas': g.faltas_total,
        }

    return render(request, 'Escola/inicio.html', {
        'matriculas': matriculas,
        'disciplinas': disciplinas,
        'dados_por_matricula': dados_por_matricula,
        'conteudo_page': 'ApuraçãoFinal',
        'title_page': f'APURAÇÃO FINAL'
    })
