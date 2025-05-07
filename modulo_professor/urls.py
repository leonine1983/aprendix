from django.urls import path
from .views import home_professor,home_sessaoIniciada, criaNotasComposicao, atualizaRecuperaFinal, registrar_presenca_diaria_view, selecionaTurma, registrar_presenca_por_aula_view

app_name = 'modulo_professor'

urlpatterns = [
    path('', home_professor, name='homeProfessor'),
    path('/sessao/', home_sessaoIniciada, name='sessaoEscola'),
    path('notas/criar/<int:aluno>/<int:grade>/<int:trimestre>', criaNotasComposicao, name='criaNotasComposicao'),
    path('recuperacao-final/<int:pk>/<int:grade>/', atualizaRecuperaFinal, name='atualiza_recuperacao_final'),

    path('presenca/diaria/seleciona/', selecionaTurma, name='selecionaTurmaFalta'),
    path('presenca/diaria/<int:turma_id>/', registrar_presenca_diaria_view, name='presenca_diaria'),

    path('presenca/aula/<int:turma_disciplina_id>/', registrar_presenca_por_aula_view, name='presenca_por_aula'),
    #path('sucesso/', lambda request: render(request, 'sucesso.html'), name='sucesso'),

]
