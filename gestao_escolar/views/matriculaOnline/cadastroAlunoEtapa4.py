from django.shortcuts import render, redirect
from gestao_escolar.models import Alunos
from django.contrib.auth.decorators import login_required
from .matricualOnline_form import MatriculaOnline_etapa4
from django.contrib import messages


@login_required
def cadastro_aluno_etapa4(request, aluno_id):
    aluno = Alunos.objects.get(id=aluno_id)
    form = MatriculaOnline_etapa4(request.POST or None, instance=aluno)
    if request.method == 'POST':

        # Aqui você pode adicionar mais dados, como dados de saúde, escolaridade, etc.
        aluno.tipo_sanguineo = request.POST.get('tipo_sanguineo')
        aluno.deficiencia_aluno_id = request.POST.get('deficiencia_aluno')
        aluno.save()
        messages.success(request, f"As informações foram atualizadas com sucesso: RG e CPF. A partir de agora, você atualizarar os dados da Certidão de Nascimento do aluno.")
        return redirect('matricula_online', aluno_id=aluno.id)
   
    
    return render(request, 'Escola/matriculaOnline/etapa4.html', {'aluno': aluno, 'form':form})
