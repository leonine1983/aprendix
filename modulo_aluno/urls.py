from django.urls import path
from .views import home_aluno, update_perfil_aluno
app_name = 'modulo_aluno'

urlpatterns = [
    path('', home_aluno, name='homeAluno'),
    path('perfil/atualizar/', update_perfil_aluno, name='update_perfil_aluno')
]
