from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from gestao_escolar.models import (
    MatriculasOnline, Matriculas, Alunos, Bairro, 
    EscolaMatriculaOnline, GestaoTurmas
)
from rh.models import Ano, Prefeitura


@login_required
def home_aluno(request):
    userAluno = request.user.userAluno_related
    request.session['alunoUser'] = userAluno.id  
    aluno_id = userAluno.aluno.id    
    prefeitura = Prefeitura.objects.all().first()

    # Ano letivo atual (o mais recente)
    ano_atual = Ano.objects.order_by('-ano').first()

    # Busca matrícula atual do aluno
    matricula = Matriculas.objects.filter(
        aluno=aluno_id,
        turma__ano_letivo=ano_atual
    ).first()

    # Se não achar, tenta o ano anterior
    if not matricula:
        ano_anterior = Ano.objects.filter(ano__lt=ano_atual.ano).order_by('-ano').first()
        if ano_anterior:
            matricula = Matriculas.objects.filter(
                aluno=aluno_id,
                turma__ano_letivo=ano_anterior
            ).first()

    # Todas as matrículas do aluno
    matriculas = Matriculas.objects.filter(aluno=aluno_id)

    # Matrícula online
    aluno_matricula_online = MatriculasOnline.objects.filter(aluno=aluno_id)

    # Dados complementares
    aluno = Alunos.objects.get(id=aluno_id)
    bairro = get_object_or_404(Bairro, nome_bairro=aluno.bairro)
    escola_bairro = EscolaMatriculaOnline.objects.filter(
        Q(ativo=True) &
        (Q(escola__related_dadosEscola__bairro__id=bairro.id) |
         Q(escola__related_dadosEscola__bairro_atendEscola__id=bairro.id))
    )

    # Busca todos os registros de notas/faltas/pareceres do aluno
    gestao_aluno = (
        GestaoTurmas.objects
        .filter(aluno__aluno=aluno)
        .select_related('grade__disciplina', 'trimestre')
        .order_by('grade__disciplina__ordem_historico', 'trimestre__numero_nome')
    )

    # Organiza os dados em estrutura hierárquica: disciplina → trimestres
    dados_disciplinas = {}
    for registro in gestao_aluno:
        disciplina_nome = registro.grade.disciplina.nome if registro.grade else "Sem disciplina"
        trimestre_nome = registro.trimestre.numero_nome if registro.trimestre else "Trimestre não definido"

        if disciplina_nome not in dados_disciplinas:
            dados_disciplinas[disciplina_nome] = []

        dados_disciplinas[disciplina_nome].append({
            'trimestre': trimestre_nome,
            'nota': registro.notas,
            'faltas': registro.faltas,
            'parecer': registro.parecer_descritivo,
        })

    # Se não há matrícula em nenhum ano, exibe página reduzida
    if not matricula:
        return render(request, 'modulo_aluno/home.html', {
            'aluno': aluno_matricula_online,
            'matricula_atual': None,
            'matriculas': matriculas,
            'prefeitura': prefeitura,
            'alunoM': aluno,
            'aluno_matricula_online': aluno_matricula_online,
            'escola_bairro': escola_bairro,
        })

    # Contexto final
    contexto = {
        'aluno': aluno_matricula_online,
        'matricula_atual': matricula,
        'matriculas': matriculas,
        'prefeitura': prefeitura,
        'alunoM': aluno,
        'aluno_matricula_online': aluno_matricula_online,
        'escola_bairro': escola_bairro,
        'dados_disciplinas': dados_disciplinas,  # <<<<<< DADOS PARA O TEMPLATE
    }

    return render(request, 'modulo_aluno/home.html', contexto)
