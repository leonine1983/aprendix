from django.urls import path
from gestao_escolar.views.GE_pasta_escola import *
from gestao_escolar.views.pasta_session import *
from gestao_escolar.views import *
from gestao_escolar.views.views import   Pagina_inicio


urlpatterns = [

# Matricula Online - Area Publica
    path('matricula_online/', pesquisar_aluno, name='pesquisar_aluno'),
    path('cadastro_aluno/<str:nome>/<str:mae>/<str:cpf>', cadastro_aluno_etapa1, name='cadastro_aluno_etapa1'),
    path('cadastro_aluno/exibe/dados/acesso/<int:aluno_id>', cadastro_aluno_etapa1_exibeSenha, name='cadastro_aluno_etapa1_exibeSenha'),    
    path('cadastro_aluno/etapa2/documentos/endereco/<int:aluno_id>', cadastro_aluno_etapa2, name='cadastro_aluno_etapa2'),
    path('cadastro_aluno/etapa3/<int:aluno_id>', cadastro_aluno_etapa3, name='cadastro_aluno_etapa3'),
    path('cadastro_aluno/certidao/<int:aluno_id>', cadastro_aluno_etapa4, name='cadastro_aluno_etapa4'),
    path('cadastro_aluno/fisicoEsaude/<int:aluno_id>', cadastro_aluno_etapa5, name='cadastro_aluno_etapa5'),
]