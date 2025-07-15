from django.urls import path
from docsGestao_Escolar.views import *

app_name = "docsGestao_escolar"

urlpatterns = [
    path('docs/boletim/', boletim, name='boletim'),    
    path('docs/boletim/turma/<int:turma_id>', boletim_matriculas, name='boletim_turma'),    
    path('docs/boletim/turma/trimestral/<int:aluno_id>/<int:turma_id>', boletim_trimestral, name='boletim_trimestral'),    
]