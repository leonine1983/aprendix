# modulo_Merendeiras/urls.py

from django.urls import path
from . import views

app_name = "modulo_merendeiras"

urlpatterns = [

    path("dashboard/", views.DashboardMerendeiraView.as_view(), name="dashboard_merendeira"),
    path(
        "configuracoes/",
        views.ConfiguracaoPessoalUpdateView.as_view(),
        name="configuracao_pessoal",
    ),
    
    # ROTAS USADAS ------------------------------------------------
    path("estoque/", views.EstoqueEscolaListView.as_view(), name="estoque_list_escola" ),

    # Execução do Cardápio do Dia
    path("", views.CardapioHojeView.as_view(), name="cardapio_hoje"),
    path("receita/<int:pk>/", views.ReceitaDetailView.as_view(), name="receita_detail"),
    path("cardapio/hoje/cozinha", views.CardapioHojeView.as_view(), name="cardapio_hoje" ),
    path("cardapio/executar/", views.PrepararExecucaoView.as_view(), name="preparar_execucao" ),
    path("cardapio/execucao/<int:execucao_id>/ficha/<str:turno>/", views.FichaDiariaCreateView.as_view(), name="ficha_diaria" ),
    path("cardapio/execucao/<int:pk>/", views.ExecucaoCardapioDetailView.as_view(), name="execucao_detalhe"  ),
    path("cardapio/execucao/<int:pk>/finalizar/", views.FinalizarExecucaoView.as_view(), name="finalizar_execucao" ),
    path("cardapio/execucao/<int:execucao_pk>/item/<int:item_pk>/cancelar/", views.CancelarReceitaView.as_view(), name="cancelar_receita" ),

    # Estoque Escolar
    path("estoque/", views.EstoqueEscolaListView.as_view(), name="estoque_lista"),

    # 📊 Listagem de movimentações
    path("estoque/movimentacoes/", views.MovimentacaoEstoqueListView.as_view(), name="movimentacao_estoque_list"),

    # Descartes Escola
    path("estoque/<int:pk>/descartar/", views.DescartarEstoqueView.as_view(), name="descartar_estoque" ),   
    path("estoque/descartes/", views.ListaDescartesView.as_view(), name="lista_descartes_escola" ), 

    # 📦 Transferências ----------------------------------------
    path("transferencias/escola/",  views.TransferenciasEscolaListView.as_view(), name="transferencias_recebidas"),
    path("transferencias/escola/conferir/<int:pk>/iniciar/", views.ReceberTransferenciaView.as_view(), name="escola_receber_transfe"),
    path("transferencia/escola/<int:pk>/conferencia/", views.TransferenciaConferenciaView.as_view(), name="transferencia_conferencia_escola"),
    path("transferencias/escola/<int:pk>/", views.TransferenciaEscolaDetailView.as_view(), name="transferencia_detalhe_escola" ),   

    # FIM ROTAS USADAS ------------------------------------------------

    path("receitas/", views.ReceitaListView.as_view(), name="receita_lista"),
    path("receitas/nova/", views.ReceitaCreateView.as_view(), name="receita_nova"),
    path("receitas/<int:pk>/", views.ReceitaDetailView.as_view(), name="receita_detalhe"),

    path("execucoes/", views.ExecucaoListView.as_view(), name="execucao_lista"),
    path("execucoes/<int:pk>/executar/", views.ExecutarReceitaView.as_view(), name="executar_receita"), 
    
    path("cozinha/execucoes/", views.ExecucaoListView.as_view(), name="lista_execucoes"),
      
    path("cozinha/execucao/<int:pk>/", views.PainelExecucaoView.as_view(), name="painel_execucao"),
    

    # COZINHA - EXCECUÇAÕ DAS RECEITAS
    # 🔍 Detalhe da movimentação
    path("cozinha/movimentacoes/", views.PainelExecucaoView.as_view(), name="cozinha_merenda"
    ),


    
    
    
    


]