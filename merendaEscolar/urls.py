from django.urls import path, include
from . views import *



app_name = 'merendaEscolar'
urlpatterns = [    
    #path('', inicio_merenda, name='merenda_inicio'),  
    path('', EstoqueCentralListView, name='merenda_inicio'),  
    path("unidades/", UnidadeMedidaListView.as_view(), name="unidade_medida_list"),
    path("unidades/nova/", UnidadeMedidaCreateView.as_view(), name="unidade_medida_create"),
    path("unidades/<int:pk>/editar/", UnidadeMedidaUpdateView.as_view(), name="unidade_medida_update"),

    # Categoria
    path("categorias/", CategoriaProdutoListView.as_view(), name="categoria_produto_list"),
    path("categorias/nova/", CategoriaProdutoCreateView.as_view(), name="categoria_produto_create"),
    path("categorias/<int:pk>/editar/", CategoriaProdutoUpdateView.as_view(), name="categoria_produto_update"),

    # Produto
    path("produtos/", ProdutoListView.as_view(), name="produto_list"),
    path("produtos/novo/", ProdutoCreateView.as_view(), name="produto_create"),
    path("produtos/<int:pk>/editar/", ProdutoUpdateView.as_view(), name="produto_update"),

    # Estoque ----------------
     # Dashboard / Listagem
    path(
        "central/",
        EstoqueCentralListView.as_view(),
        name="estoque-central"
    ),

    # Entrada de produtos no estoque central
    path(
        "central/entrada/",
        EntradaEstoqueCentralView.as_view(),
        name="entrada-central"
    ),

    # Transferencias
    path(
        "transferencias/",
        TransferenciaListView.as_view(),
        name="transferencia-list"
    ),

    path(
        "transferencia/<int:pk>/",
        TransferenciaDetailView.as_view(),
        name="transferencia-detail"
    ),

    path(
        "transferencia/<int:pk>/enviar/",
        TransferenciaEnviarView.as_view(),
        name="transferencia-enviar"
    ),

    path(
        "transferencia/<int:pk>/receber/",
        TransferenciaReceberView.as_view(),
        name="transferencia-receber"
    ),

    path(
    "transferencias/nova/",
    TransferenciaCreateView.as_view(),
    name="transferencia-create"
    ),

    path(
    "transferencia/<int:pk>/item/novo/",
    TransferenciaItemCreateView.as_view(),
    name="transferenciaitem-create"
    ),

    # Escola 
    path(
        "escola/<int:escola_id>/estoque/",
        EstoqueEscolaDashboardView.as_view(),
        name="estoque_escola_dashboard"
    ),
    path('escolas/', ListaEscolasRecebimentoView.as_view(), name='lista_escolas'),
    path('escola/<int:escola_id>/', TransferenciasAbertasEscolaView.as_view(), name='transferencias_abertas'),
    path('receber/<int:pk>/', ReceberTransferenciaView.as_view(), name='escola_receber'),
    path(
        "transferencia/<int:pk>/conferencia/",
        TransferenciaConferenciaView.as_view(),
        name="transferencia_conferencia"
    ),

    path('escolas/dashboard', ListaEscolasView.as_view(), name='lista_escolas_dashboard'),
    path('escola/<int:escola_id>/estoque/', EstoqueEscolaDashboardView.as_view(), name='estoque_escola_dashboard'),

    # RECEITA  
    path("receita/", ReceitaListView.as_view(), name="receita_lista"),
    path("nova/", ReceitaCreateView.as_view(), name="receita_criar"),
    path("<int:pk>/", ReceitaDetailView.as_view(), name="receita_detalhe"),
    path("<int:pk>/editar/", ReceitaUpdateView.as_view(), name="receita_editar"),
    path("<int:pk>/excluir/", ReceitaDeleteView.as_view(), name="receita_excluir"),
     
    
]