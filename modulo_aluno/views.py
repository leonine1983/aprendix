from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from gestao_escolar.models import MatriculasOnline, Matriculas, Alunos, Bairro, EscolaMatriculaOnline
from rh.models import Ano, Prefeitura
from django.db.models import Q


@login_required
def home_aluno(request):
    userAluno = request.user.userAluno_related
    request.session['alunoUser'] = userAluno.id  
    aluno = userAluno.aluno.id
    prefeitura = Prefeitura.objects.all().first()

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


    # VERIFICA SE O ALUNO TEM MATRICULA ONLINE EM ABERTO
    aluno = Alunos.objects.get(id=aluno)
    # Verifica se o aluno fez a matricula online anteriormente     
    aluno_bairro = aluno.bairro
    bairro = get_object_or_404(Bairro, nome_bairro = aluno_bairro)
    escola_bairro = EscolaMatriculaOnline.objects.filter(
    Q(ativo = True) &
    Q(escola__related_dadosEscola__bairro__id=bairro.id) |
    Q(escola__related_dadosEscola__bairro_atendEscola__id=bairro.id)
    )    
    
    aluno_matricula_online = MatriculasOnline.objects.filter(aluno = aluno)
    print(f"aluno {aluno_matricula_online}")
   





    # Se não achou matrícula em nenhum ano
    if not matricula:
        return render(request, 'modulo_aluno/home.html', {
            'aluno': alunoMatricula,
            'matricula_atual': None,
            'matriculas': matriculas,
            'prefeitura': prefeitura,

            # verifica se tem matricula online em aberto
            'alunoM': aluno,
            'aluno_matricula_online':aluno_matricula_online,
            'escola_bairro':escola_bairro
        })

    return render(request, 'modulo_aluno/home.html', {
        'aluno': alunoMatricula,
        'matricula_atual': matricula,
        'matriculas': matriculas,

        # verifica se tem matricula online em aberto
        'alunoM': aluno,
        'aluno_matricula_online':aluno_matricula_online,
        'escola_bairro':escola_bairro

        
    })
