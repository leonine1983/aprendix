from django.shortcuts import render, redirect
from gestao_escolar.models import Alunos

def cadastro_aluno_etapa3(request, aluno_id):
    aluno = Alunos.objects.get(id=aluno_id)
    if request.method == 'POST':
        # Aqui você pode adicionar mais dados, como dados de saúde, escolaridade, etc.
        aluno.tipo_sanguineo = request.POST.get('tipo_sanguineo')
        aluno.deficiencia_aluno_id = request.POST.get('deficiencia_aluno')
        aluno.save()
        return redirect('matricula_online', aluno_id=aluno.id)
    
    return render(request, 'cadastro_aluno/etapa3.html', {'aluno': aluno})
