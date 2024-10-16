from rh.models import Ano, Escola
from gestao_escolar.models import Turmas, Matriculas, GestaoTurmas, Trimestre
from django.shortcuts import render

def boletim_matriculas(request, turma_id):
    turmas = Turmas.objects.get(id = turma_id)
    matricula_boletim = Matriculas.objects.filter(turma = turmas)

    context = {
        'conteudo_page':"boletim_aluno",
        'matriculas' : matricula_boletim
    }
    return render(request, 'Escola/inicio.html', context)


