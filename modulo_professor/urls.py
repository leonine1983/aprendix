from django.urls import path
from .views import home_professor,home_sessaoIniciada
app_name = 'modulo_professor'

urlpatterns = [
    path('', home_professor, name='homeProfessor'),
    path('/sessao/', home_sessaoIniciada, name='sessaoEscola')
]
