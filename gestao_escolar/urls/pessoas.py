from django.urls import path
from gestao_escolar.views.GE_pasta_escola import *
from gestao_escolar.views.pasta_session import *
from gestao_escolar.views import *
from gestao_escolar.views.views import   Pagina_inicio


urlpatterns = [
    path('ajax/get-cidades/', get_cidades, name='ajax_get_cidades'),
    path('ajax/get-bairros/', get_bairros, name='ajax_get_bairros'),
]