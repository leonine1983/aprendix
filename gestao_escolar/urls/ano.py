from django.urls import path
from gestao_escolar.views.ano_letivo import *

urlpatterns = [ 
    path('novo/', cria_ano, name='cria_ano'),
    path('ano/editar/<int:ano_id>/', editar_ano, name='editar_ano'),
]