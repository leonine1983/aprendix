from django.shortcuts import render, redirect
from gestao_escolar.models import Alunos

def cadastro_aluno_etapa2(request, aluno_id):
    aluno = Alunos.objects.get(id=aluno_id)
    if request.method == 'POST':
        # Aqui você pode adicionar mais dados, como telefone, endereço, etc.
        aluno.tel_celular_aluno = request.POST.get('tel_celular_aluno')
        aluno.email = request.POST.get('email')
        aluno.rua = request.POST.get('rua')
        aluno.bairro_id = request.POST.get('bairro')
        aluno.cidade_id = request.POST.get('cidade')
        aluno.save()
        return redirect('cadastro_aluno_etapa3', aluno_id=aluno.id)
    
    return render(request, 'cadastro_aluno/etapa2.html', {'aluno': aluno})
