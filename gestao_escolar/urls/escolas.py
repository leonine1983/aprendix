from django.urls import path
from gestao_escolar.views.GE_pasta_escola import *
from gestao_escolar.views.pasta_session import *
from gestao_escolar.views import *
from gestao_escolar.views.views import   Pagina_inicio


urlpatterns = [
    path('gestao_escolar', ListView_Escola.as_view(), name="GE_inicio"),    
    path('escolas/selecionar/<int:pk>/', Seleciona_escola, name='escola-selecionar'),
    path('gestao_escolar/anoLetivo', Seleciona_anoLetivo.as_view(), name="GE_anoLetivo"),
    path('anoLetivo/selecionar/<int:pk>/', seleciona_anoLetivo_session, name='selecionar-ano'),

    
    # A parti daqui o desenvolvimento da escola inicia
    path('gestao_escolar/Escola/', Pagina_inicio.as_view(), name="GE_Escola_inicio"),
    
    # Dados escola
    path('gestao_escolar/Escola/Create', CreateEscola.as_view(), name="CreateEscola"),
    path('gestao_escolar/Escola/Dados/Update/<int:pk>', UpdateEscolaDados.as_view(), name="UPdateEscolaDados"),
    path('gestao_escolar/Escola/<int:pk>', UpdateEscola.as_view(), name="DadosEscola"),
] 
