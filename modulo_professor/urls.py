from django.urls import path, re_path
from .views import *
app_name = 'modulo_professor'

urlpatterns = [
    path('', home_professor, name='homeProfessor'),
    path('/sessao/', home_sessaoIniciada, name='sessaoEscola'),
    path('/notas/criar/<int:aluno>/<int:grade>/<int:trimestre>', criaNotasComposicao, name='criaNotasComposicao'),
    path('/recuperacao-final/<int:pk>/<int:grade>/', atualizaRecuperaFinal, name='atualiza_recuperacao_final'),

    path('/presenca/diaria/seleciona/', selecionaTurma, name='selecionaTurmaFalta'),
    path('/presenca/diaria/<int:turma_id>/', registrar_presenca_diaria_view, name='presenca_diaria'),
    path('/turma/<int:turma_id>/presencas/<str:data_str>/', lista_presenca_diaria_view, name='lista_presenca_diaria'),

    path('/faltas/<int:matricula_id>/', historico_faltas_view, name='historico_faltas'),

    
    path('/presenca/diaria/seleciona/disciplina', selecionaTurmaDisciplina, name='selecionaTurmaFaltaDisciplina'),
    path('/presenca/aula/<int:turma_disciplina_id>/', registrar_presenca_por_aula_view, name='presenca_por_aula'),
    path('/faltas/<int:turma_disciplina_id>/disciplina', faltas_por_disciplina_mes_view, name='faltas_por_disciplina_mes'),
    #path('historico-faltas/<int:matricula_id>/<int:turma_disciplina_id>/', historico_faltasPAula_view, name='historico_faltas'),
    #path('sucesso/', lambda request: render(request, 'sucesso.html'), name='sucesso'),

    # Parecer descritivo
    path('/turma/parecer/<int:turma>/turma', parecerTurma, name='parecerTurma'),
    path('/aluno/<int:pk>/trimestre/<int:trimestre>/', alunoGestaoTurmasParecer, name='aluno_parecer'),

    # Diario de classe
    path('planos-de-aula/novo/', PlanoDeAulaCreateView.as_view(), name='plano_de_aula_criar'),
    path('planos-de-aula/<int:pk>/editar/', PlanoDeAulaUpdateView.as_view(), name='plano_de_aula_editar'),
    path('planos-de-aula/<int:pk>/excluir/', PlanoDeAulaDeleteView.as_view(), name='plano_de_aula_excluir'),
    path('aulas-do-dia/', aulas_do_dia, name='aulas_do_dia'),

    # AULA DIA
    path('aulas/nova/', AulaDadaCreateView.as_view(), name='aula_dada_criar'),
    path('aulas/<int:pk>/', AulaDadaDetailView.as_view(), name='aula_dada_detalhe'),
    path('aulas/<int:pk>/anexo/', AnexoAulaCreateView.as_view(), name='anexo_aula_criar'),
    path('aula/<int:aula_id>/', detalhar_aula, name='detalhar_aula'),

    # Calendário
    path('horario/professor/<int:turma_disciplina_id>', dias_de_aula_professor, name='dias_de_aula_professor'),
]
