from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from gestao_escolar.models import TurmaDisciplina


# Create your views here.
@login_required
def home_professor(request):
    userProfessor = request.user.related_vinculoUserPessoa
    request.session['professorUser'] = userProfessor
    pessoa = userProfessor.pessoa.id

    # Pequisa pra verifica se existe matricula feita do aluno
    professorGrade = TurmaDisciplina.objects.filter(professor__encaminhamento__contratado__id=pessoa)

    return render(request, 'modulo_professor/base.html', {'professor':professorGrade})
