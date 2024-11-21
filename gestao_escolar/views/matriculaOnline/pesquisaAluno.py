from django.shortcuts import render, redirect
from gestao_escolar.models import Alunos, MatriculasOnline
from django.db.models import Q

def pesquisar_aluno(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        data_nascimento = request.POST.get('data_nascimento')
        nome_mae = request.POST.get('nome_mae')

        alunos = Alunos.objects.filter(
            Q(nome_completo__icontains=nome) &
            Q(data_nascimento=data_nascimento) &
            Q(nome_mae__icontains=nome_mae)
        )

        if alunos.exists():
            return render(request, 'matricula_online/resultados_aluno.html', {'alunos': alunos})
        else:
            return redirect('cadastro_aluno_etapa1')

    return render(request, 'Escola/matriculaOnline/pesquisar_aluno.html')
