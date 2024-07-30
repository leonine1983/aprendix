from django.shortcuts import render
from gestao_escolar.models import Trimestre, Matriculas, TurmaDisciplina



def gestao_turmas_update_view(request, pk):
    matriculas = Matriculas.objects.filter(turma=pk)
    trimestres = Trimestre.objects.all()
    disciplinas = TurmaDisciplina.objects.filter(turma=pk)

    context = {
        'matriculas': matriculas,
        'trimestre': trimestres,
        'disciplinas': disciplinas,
        'conteudo_page': f"Gestão Turmas - Notas Aluno",
    }
       
    return render(request, 'Escola/inicio.html', context)

