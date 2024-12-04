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
        # Aqui você pode adicionar mais dados, como dados de saúde, escolaridade, etc.
        aluno.espectro_autista = request.POST.get('espectro_autista')
        aluno.deficiencia_aluno = request.POST.get('deficiencia_aluno')
        aluno.tipo_sanguineo = request.POST.get('tipo_sanguineo')
        aluno.deficiencia_aluno = request.POST.get('necessita_edu_especial')
        aluno.vacina_covid_19 = request.POST.get('vacina_covid_19')
        aluno.dose_vacina_covid_19 = request.POST.get('dose_vacina_covid_19')
        aluno.sindrome_de_Down = request.POST.get('sindrome_de_Down')
        aluno.save()
        messages.success(request, f"As informações foram atualizadas com sucesso: RG e CPF. A partir de agora, você atualizarar os dados da Certidão de Nascimento do aluno.")
        return redirect('matricula_online', aluno_id=aluno.id)      
    
    return render(request, 'Escola/matriculaOnline/etapa5.html', {'aluno': aluno, 'form':form})
