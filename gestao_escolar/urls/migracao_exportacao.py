from django.urls import path
from gestao_escolar.views.GE_pasta_escola import *
from gestao_escolar.views.pasta_session import *
from gestao_escolar.views import *

urlpatterns = [
    path("exportar-turmas/", exportar_turmas, name="exportar_turmas"),
] 


