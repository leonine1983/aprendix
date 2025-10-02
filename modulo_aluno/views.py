from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from gestao_escolar.models import MatriculasOnline, Matriculas
from rh.models import Ano


@login_required
def home_aluno(request):
    userAluno = request.user.userAluno_related
    request.session['alunoUser'] = userAluno.id  
    aluno = userAluno.aluno.id

    # Pega o ano letivo atual (assumindo que o mais recente é o primeiro)
    ano_atual = Ano.objects.order_by('-ano').first()

    matricula = Matriculas.objects.filter(
        aluno=aluno,
        turma__ano_letivo=ano_atual
    ).first()

    # Se não achar, busca do ano anterior
    if not matricula:
        ano_anterior = Ano.objects.filter(ano__lt=ano_atual.ano).order_by('-ano').first()
        if ano_anterior:
            matricula = Matriculas.objects.filter(
                aluno=aluno,
                turma__ano_letivo=ano_anterior
            ).first()

    # Todas as matrículas do aluno
    matriculas = Matriculas.objects.filter(aluno=aluno)

    # Verifica matrícula online
    alunoMatricula = MatriculasOnline.objects.filter(aluno=aluno)

    # Se não achou matrícula em nenhum ano
    if not matricula:
        return render(request, 'modulo_aluno/home.html', {
            'aluno': alunoMatricula,
            'matricula_atual': None,
            'matriculas': matriculas
        })

    return render(request, 'modulo_aluno/home.html', {
        'aluno': alunoMatricula,
        'matricula_atual': matricula,
        'matriculas': matriculas
    })
