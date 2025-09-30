from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from gestao_escolar.models import MatriculasOnline, Matriculas
from rh.models import Ano


# Create your views here.
@login_required
def home_aluno(request):
    userAluno = request.user.userAluno_related
    request.session['alunoUser'] = userAluno.id  
    aluno = userAluno.aluno.id
    ano = Ano.objects.all().first()
    matricula = Matriculas.objects.get(aluno = aluno, turma__ano_letivo = ano)   
    matriculas = Matriculas.objects.filter(aluno = aluno)   

    # Pequisa pra verifica se existe matricula feita do aluno
    alunoMatricula = MatriculasOnline.objects.filter(aluno=aluno)

    return render(request, 'modulo_aluno/base.html', {
        'aluno':alunoMatricula,
        'matricula_atual':matricula,
        'matriculas':matriculas})

