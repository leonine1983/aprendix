
from gestao_escolar.models import GestaoTurmas, Matriculas, TurmaDisciplina, Trimestre
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from gestao_escolar.models import GestaoTurmas, Matriculas, TurmaDisciplina, Trimestre

@login_required
def notas_usa_dialog(request, matricula, grade, trimestre, nota):    
    aluno = get_object_or_404(Matriculas, pk=matricula)
    disciplina = get_object_or_404(TurmaDisciplina, pk=grade)
    trimestre_nota = get_object_or_404(Trimestre, pk=trimestre)
    profissional_resp = f'{request.user}'

    # Atualiza se já existir, cria se não existir
    gestao_turma, created = GestaoTurmas.objects.update_or_create(
        aluno=aluno,
        grade=disciplina,
        trimestre=trimestre_nota,
        defaults={
            "notas": nota,
            "profissional_resp": profissional_resp
        }
    )
    # Para garantir uma unica mensagem por nota salva
    messages.set_level(request, messages.constants.SUCCESS)
    messages.success(request, f"Nota do aluno {aluno} para o {trimestre}º TRIMESTRE, atualizada com sucesso")

    return redirect("Gestao_Escolar:gestao_turmas_update", pk=aluno.turma.pk)


