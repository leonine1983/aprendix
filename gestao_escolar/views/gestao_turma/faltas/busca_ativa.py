from gestao_escolar.models import Matriculas, GestaoTurmas, TurmaDisciplina

def obter_alunos_risco_evasao(request):
    """
    Função para identificar alunos em risco de evasão escolar, usando ano letivo e escola da sessão.

    Critérios de risco:
    - Alunos com mais de 15% de faltas em relação à carga horária anual da disciplina.
    
    Retorna:
    - Lista de alunos em risco com detalhes de turma, disciplina, faltas, notas e percentual de faltas.
    - Contexto com título e descrição pronto para uso em views.
    """

    # Obter dados diretamente da sessão
    ano = request.session.get('anoLetivo_id')
    escola_id = request.session.get('escola_id')

    if not ano or not escola_id:
        return {
            'title': "Alunos em risco de evasão escolar",
            'descricao': "Ano letivo ou escola não definidos na sessão.",
            'alunos_em_risco': []
        }

    # Buscar alunos matriculados no ano e na escola
    matriculas = Matriculas.objects.filter(
        turma__ano_letivo_id=ano,
        turma__escola_id=escola_id
    ).select_related('turma', 'aluno')

    alunos_em_risco = []

    for matricula in matriculas:
        gestao_turmas = GestaoTurmas.objects.filter(
            aluno=matricula,
            grade__turma=matricula.turma
        ).select_related('grade', 'grade__disciplina', 'trimestre')

        for registro in gestao_turmas:
            if not registro.faltas_total or not registro.grade.carga_horaria_anual:
                continue  # Ignora registros sem dados suficientes

            percentual_faltas = (registro.faltas_total / registro.grade.carga_horaria_anual) * 100

            if percentual_faltas >= 15:  # Alerta de risco
                alunos_em_risco.append({
                    'aluno': matricula.aluno.nome_completo,
                    'turma': matricula.turma.nome,
                    'disciplina': registro.grade.disciplina.nome,
                    'faltas': registro.faltas_total,
                    'carga_horaria_anual': registro.grade.carga_horaria_anual,
                    'percentual_faltas': round(percentual_faltas, 2),
                    'notas': registro.notas
                })

    contexto = {
        'title': "Alunos em risco de evasão escolar",
        'descricao': (
            "Alunos que possuem mais de 15% de faltas em relação à carga horária anual da disciplina "
            "são considerados em risco de evasão. Recomenda-se intervenção pedagógica, contato com responsáveis "
            "e acompanhamento contínuo para evitar abandono escolar."
        ),
        'alunos_em_risco': alunos_em_risco
    }

    return contexto
