from django.urls import path
from .views import home_aluno
app_name = 'modulo_aluno'

urlpatterns = [
    path('', home_aluno, name='homeAluno')
]
