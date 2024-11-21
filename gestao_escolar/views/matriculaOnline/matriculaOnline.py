from django.shortcuts import render, redirect
from gestao_escolar.models import Alunos, MatriculasOnline
from django.db.models import Q


def matricular_aluno(request, aluno_id):
    aluno = Alunos.objects.get(id=aluno_id)
    if request.method == 'POST':
        # Aqui você pode criar o objeto de matrícula
        matricula = MatriculasOnline.objects.create(
            aluno=aluno,
            serie=request.POST.get('serie'),
            ano_letivo=request.POST.get('ano_letivo'),
            escola=request.POST.get('escola')
        )
        matricula.save()
        return render(request, 'matricula_online/matricula_confirmada.html', {'aluno': aluno})

    return render(request, 'Escola/matriculaOnline/matricular_aluno.html', {'aluno': aluno})
