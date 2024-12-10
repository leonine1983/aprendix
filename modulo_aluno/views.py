from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from gestao_escolar.models import MatriculasOnline


# Create your views here.
@login_required
def home_aluno(request):
    userAluno = request.user.userAluno_related
    request.session['alunoUser'] = userAluno

    aluno = userAluno.aluno.id

    # Pequisa pra verifica se existe matricula feita do aluno
    alunoMatricula = MatriculasOnline.objects.filter(aluno=aluno)

    return render(request, 'modulo_aluno/base.html', {'aluno':alunoMatricula})
