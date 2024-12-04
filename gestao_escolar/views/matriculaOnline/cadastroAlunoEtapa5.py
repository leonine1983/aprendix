from django.shortcuts import render, redirect
from gestao_escolar.models import Alunos
from django.contrib.auth.decorators import login_required
from .matricualOnline_form import MatriculaOnline_etapa5
from django.contrib import messages


@login_required
def cadastro_aluno_etapa5(request, aluno_id):
    aluno = Alunos.objects.get(id=aluno_id)
    form = MatriculaOnline_etapa5(request.POST or None, instance=aluno)
    if request.method == 'POST':
        if form.is_valid():
            # Aqui você pode adicionar mais dados, como dados de saúde, escolaridade, etc.
            aluno.espectro_autista = form.cleaned_data['espectro_autista']
            aluno.deficiencia_aluno = form.cleaned_data['deficiencia_aluno']
            aluno.tipo_sanguineo = form.cleaned_data['tipo_sanguineo']
            aluno.deficiencia_aluno = form.cleaned_data['necessita_edu_especial']
            aluno.vacina_covid_19 = form.cleaned_data['vacina_covid_19']
            aluno.dose_vacina_covid_19 = form.cleaned_data['dose_vacina_covid_19']
            aluno.sindrome_de_Down = form.cleaned_data['sindrome_de_Down']
            aluno.save()
            messages.success(request, f"As informações foram atualizadas com sucesso: Fisicos e Biológicos. A partir de agora, você já pode realizar a matrícula do aluno em uma das turmas disponíveis")
            return redirect('matricula_online', aluno_id=aluno.id)      
    
    return render(request, 'Escola/matriculaOnline/etapa5.html', {'aluno': aluno, 'form':form})
