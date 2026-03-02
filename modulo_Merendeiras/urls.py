# modulo_Merendeiras/urls.py

from django.urls import path
from . import views

app_name = "modulo_merendeiras"

urlpatterns = [

    path("", views.DashboardMerendeiraView.as_view(), name="dashboard"),

    path("estoque/", views.EstoqueEscolaListView.as_view(), name="estoque_lista"),

    path("receitas/", views.ReceitaListView.as_view(), name="receita_lista"),
    path("receitas/nova/", views.ReceitaCreateView.as_view(), name="receita_nova"),
    path("receitas/<int:pk>/", views.ReceitaDetailView.as_view(), name="receita_detalhe"),

    path("execucoes/", views.ExecucaoListView.as_view(), name="execucao_lista"),
    path("execucoes/<int:pk>/executar/", views.ExecutarReceitaView.as_view(), name="executar_receita"),
]