# modulo_Merendeiras/urls.py

from django.urls import path
from . import views

app_name = "modulo_merendeiras"

urlpatterns = [

    path("", views.DashboardMerendeiraView.as_view(), name="dashboard_merendeira"),

    path("estoque/", views.EstoqueEscolaListView.as_view(), name="estoque_lista"),

    path("receitas/", views.ReceitaListView.as_view(), name="receita_lista"),
    path("receitas/nova/", views.ReceitaCreateView.as_view(), name="receita_nova"),
    path("receitas/<int:pk>/", views.ReceitaDetailView.as_view(), name="receita_detalhe"),

    path("execucoes/", views.ExecucaoListView.as_view(), name="execucao_lista"),
    path("execucoes/<int:pk>/executar/", views.ExecutarReceitaView.as_view(), name="executar_receita"),


       # 📦 Transferências recebidas ESCOLA
    path(
        "transferencias/escola/",
        views.TransferenciasEscolaListView.as_view(),
        name="transferencias_recebidas"
    ),

    path(
        "transferencias/escola/conferir/<int:pk>/iniciar/",
        views.ReceberTransferenciaView.as_view(),
        name="escola_receber_transfe"        
    ),

    path(
        "transferencia/escola/<int:pk>/conferencia/",
        views.TransferenciaConferenciaView.as_view(),
        name="transferencia_conferencia_escola"
    ),

    path(
    "transferencias/escola/<int:pk>/",
    views.TransferenciaEscolaDetailView.as_view(),
    name="transferencia_detalhe_escola"
    ),

    # ESTOQUE ESCOLA ----------------------------------------------
    # 📦 Estoque da escola (visão da merendeira)
    path("estoque/", views.EstoqueEscolaListView.as_view(), name="estoque_list_escola" ),

    # Descartes Escola
    path("estoque/<int:pk>/descartar/", views.DescartarEstoqueView.as_view(), name="descartar_estoque" ),        
    path("estoque/descartes/", views.ListaDescartesView.as_view(), name="lista_descartes_escola" ),

      # 📊 Listagem de movimentações
    path(
        "estoque/movimentacoes/",
        views.MovimentacaoEstoqueListView.as_view(),
        name="movimentacao_estoque_list"
    ),

    # 🔍 Detalhe da movimentação
    path(
        "estoque/movimentacoes/<int:pk>/",
        views.MovimentacaoEstoqueDetailView.as_view(),
        name="movimentacao_estoque_detail"
    ),

    # COZINHA - EXCECUÇAÕ DAS RECEITAS
    # 🔍 Detalhe da movimentação
    path("cozinha/movimentacoes/", views.PainelExecucaoView.as_view(), name="cozinha_merenda"
    ),





]