from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from gestao_escolar.models import GestaoTurmas, Matriculas, Trimestre, TurmaDisciplina
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum

@login_required
def create_or_update_Media_turmas(request, aluno_id):
    aluno = get_object_or_404(Matriculas, pk=aluno_id)
    disciplinas = TurmaDisciplina.objects.filter(turma=aluno.turma.id)
    trimestre = Trimestre.objects.get(id=4)

    # Criar registros automaticamente ao carregar a página
    for disciplina in disciplinas:
        gestao_turma, created = GestaoTurmas.objects.get_or_create(aluno=aluno, trimestre=trimestre, grade=disciplina)
        if created:
            gestao_turma.profissional_resp = request.user.username
            gestao_turma.data_hora_mod = timezone.now()

            notas_aluno = GestaoTurmas.objects.filter(aluno=aluno, grade=disciplina).aggregate(Sum('notas'))
            total_notas = notas_aluno['notas__sum']

            ano_letivo = aluno.turma.ano_letivo
            trimestres = Trimestre.objects.filter(ano_letivo=ano_letivo)
            quant_trimestres = trimestres.count()

            if total_notas is not None:
                media_final = total_notas / (quant_trimestres - 1)
                gestao_turma.media_final = media_final

            gestao_turma.trimestre = trimestre
            gestao_turma.save()

    # Mensagem de sucesso
    success_message = "Médias dos alunos foram atualizadas com sucesso!"
    messages.success(request, success_message)

    return redirect(reverse('Gestao_Escolar:gestao_turmas_update', kwargs={'pk': aluno.turma.pk}))


