from django.urls import path
from .views import home_professor,home_sessaoIniciada, criaNotasComposicao, atualizaRecuperaFinal
app_name = 'modulo_professor'

urlpatterns = [
    path('', home_professor, name='homeProfessor'),
    path('/sessao/', home_sessaoIniciada, name='sessaoEscola'),
    path('notas/criar/<int:aluno>/<int:grade>/<int:trimestre>', criaNotasComposicao, name='criaNotasComposicao'),
    path('recuperacao-final/<int:pk>/<int:grade>/', atualizaRecuperaFinal, name='atualiza_recuperacao_final'),
]
