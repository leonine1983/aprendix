from django.urls import path
from core.views.conta import (
    MeuPerfilView,
    AlterarSenhaView,
    ConfiguracoesView,
    SairView,
)
from core.views.curriculoPublicoView import CurriculoPublicoView

app_name = "core"

urlpatterns = [
    path("minha-conta/", MeuPerfilView.as_view(), name="meu-perfil"),
    path("minha-conta/alterar-senha/", AlterarSenhaView.as_view(), name="alterar-senha"),
    path("minha-conta/configuracoes/", ConfiguracoesView.as_view(), name="configuracoes"),
    path("minha-conta/sair/", SairView.as_view(), name="sair"),
    path("profissional/<slug:slug>/", CurriculoPublicoView.as_view(), name="curriculo-publico"),
    
]