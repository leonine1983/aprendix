from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from gestao_escolar.models import GestaoTurmas, Matriculas, TurmaDisciplina, Trimestre


@login_required
def faltas_usa_dialog(request, matricula, grade, trimestre, falta):    
    aluno = get_object_or_404(Matriculas, pk=matricula)
    disciplina = get_object_or_404(TurmaDisciplina, pk=grade)
    trimestre_falta = get_object_or_404(Trimestre, pk=trimestre)
    profissional_resp = str(request.user)

    # 🔹 Validação rigorosa — só aceita inteiros
    try:
        falta_int = int(falta)
    except ValueError:
        messages.error(request, "O valor de faltas deve ser um número inteiro.")
        return redirect("Gestao_Escolar:gestao_turmas_update", pk=aluno.turma.pk)

    # 🔹 Atualiza ou cria o registro
    gestao_turma, created = GestaoTurmas.objects.update_or_create(
        aluno=aluno,
        grade=disciplina,
        trimestre=trimestre_falta,
        defaults={
            "faltas": falta_int,
            "profissional_resp": profissional_resp,
            "data_hora_mod": timezone.now(),
        }
    )

    # 🔹 Mensagem de sucesso
    messages.success(
        request,
        f"Faltas do aluno {aluno} no {trimestre_falta.nome if hasattr(trimestre_falta, 'nome') else trimestre_falta} atualizadas com sucesso."
    )

    return redirect("Gestao_Escolar:gestao_turmas_update", pk=aluno.turma.pk)






