from django.shortcuts import render, get_object_or_404
from gestao_escolar.models import TurmaDisciplina, Presenca
from modulo_professor.models import PlanoDeAula, AulaDada
from django.contrib.auth.decorators import login_required

@login_required
def relatorio_plano_aula_frequencia(request, plano_id):
    plano = get_object_or_404(PlanoDeAula, id=plano_id)
    turma_disciplina = plano.turma_disciplina

    aulas = plano.aulas_relacionadas.all().order_by('data', 'aula_numero')

    aulas_info = []
    for aula in aulas:
        presencas = Presenca.objects.filter(
            turma_disciplina=turma_disciplina,
            data=aula.data,
            aula_numero=aula.aula_numero
        ).select_related('matricula__aluno')

        presentes = [p.matricula.aluno.nome_completo for p in presencas if p.presente]
        ausentes = [p.matricula.aluno.nome_completo for p in presencas if not p.presente]

        aulas_info.append({
            'aula': aula,
            'presentes': presentes,
            'ausentes': ausentes,
        })

    return render(request, 'Escola/inicio.html', {
        'plano': plano,
        'turma_disciplina': turma_disciplina,
        'aulas_info': aulas_info,
        'conteudo_page': "relatorio_planoAula"
    })
