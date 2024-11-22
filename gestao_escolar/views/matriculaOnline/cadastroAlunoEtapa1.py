from django.shortcuts import render, redirect
from gestao_escolar.models import Alunos
from .matricualOnline_form import Aluno_documento_form


def cadastro_aluno_etapa1(request, nome, mae):
    form = Aluno_documento_form()
    if request.method == 'POST':
        nome_completo = request.POST.get('nome_completo')
        nome_mae = request.POST.get('nome_mae')
        data_nascimento = request.POST.get('data_nascimento')
        sexo = request.POST.get('sexo')
        
        aluno = Alunos.objects.create(
            nome_completo=nome_completo,
            nome_mae=nome_mae,
            data_nascimento=data_nascimento,
            sexo_id=sexo
        )
        aluno.save()
        return redirect('cadastro_aluno_etapa2', aluno_id=aluno.id)
    
    return render(request, 'Escola/matriculaOnline/etapa1.html', {'form':form, 'nomeAluno': nome, 'nomeMae':mae})

