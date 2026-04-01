from django.urls import path, include
from . views import *



app_name = 'merendaEscolar'
urlpatterns = [ 
    
    path('', DashboardNutricionalView.as_view()  , name='merenda_inicio'),   
    path("unidades/", UnidadeMedidaListView.as_view(), name="unidade_medida_list"),
    path("unidades/nova/", UnidadeMedidaCreateView.as_view(), name="unidade_medida_create"),
    path("unidades/<int:pk>/editar/", UnidadeMedidaUpdateView.as_view(), name="unidade_medida_update"),
    path("unidades/<int:pk>/excluir/", UnidadeMedidaDeleteView.as_view(), name="unidade_medida_delete"),

    # Categoria
    path("categorias/", CategoriaProdutoListView.as_view(), name="categoria_produto_list"),
    path("categorias/nova/", CategoriaProdutoCreateView.as_view(), name="categoria_produto_create"),
    path("categorias/<int:pk>/editar/", CategoriaProdutoUpdateView.as_view(), name="categoria_produto_update"),
    # Excluir categoria
    path(
        "categorias/<int:pk>/excluir/",
        CategoriaProdutoDeleteView.as_view(),
        name="categoria_produto_delete"
    ),

    # Produto
    path("produtos/", ProdutoListView.as_view(), name="produto_list"),
    path("produtos/novo/", ProdutoCreateView.as_view(), name="produto_create"),
    path("produtos/<int:pk>/editar/", ProdutoUpdateView.as_view(), name="produto_update"),
    path(
    "produtos/<int:pk>/excluir/", ProdutoDeleteView.as_view(), name="produto_delete"
),

    # Estoque ----------------
    path("central/",EstoqueCentralListView.as_view(), name="estoque-central"  ),

    # Entrada de produtos no estoque central
    path("central/entrada/", EntradaEstoqueCentralView.as_view(), name="entrada-central"),
    path("estoque/descarte/<int:pk>/", RegistrarDescarteView.as_view(), name="registrar-descarte",),
    path("estoque/descarte/nota/<int:pk>/", NotaDescarteView.as_view(), name="nota-descarte"),
    path("relatorios/descartes/", RelatorioDescarteListView.as_view(), name="relatorio-descartes",),
    path("descartes/<int:pk>/detalhes/", DescarteDetalhesView.as_view(), name="descarte_detalhes"),

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
    path(
    "transferencia/item/<int:pk>/excluir/",
    TransferenciaItemDeleteView.as_view(),
    name="transferenciaitem-delete"
    ),
    path(
    "transferencia/item/<int:pk>/editar/",
    TransferenciaItemUpdateView.as_view(),
    name="transferenciaitem-update"
    ),
    path(
    "transferencia/<int:pk>/imprimir/",
    TransferenciaPrintView.as_view(),
    name="transferencia-print"
    ),

    # Escola 
    path(
        "escola/<int:escola_id>/estoque/",
        EstoqueEscolaDashboardView.as_view(),
        name="estoque_escola_dashboard"
    ),
    path('escolas/', ListaEscolasRecebimentoView.as_view(), name='lista_escolas'),
    path('escola/<int:escola_id>/', TransferenciasAbertasEscolaView.as_view(), name='transferencias_abertas'),
    path('escola/receber/<int:pk>/', ReceberTransferenciaView.as_view(), name='escola_receber'),
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

    # RELATÓRIOS
     path("estoque/central/relatorios/", RelatorioEstoqueCentralView.as_view(), name="relatorio_estoque_central", ),


     # =========================
    # CARDÁPIO
    # =========================
    path("cardapios/", CardapioListView.as_view(), name="cardapio_list"),
    path("cardapio/novo/", CardapioCreateView.as_view(), name="cardapio_create"),
    path("cardapio/<int:pk>/editar/", CardapioUpdateView.as_view(), name="cardapio_update"),
    path("cardapio/<int:pk>/deletar/", CardapioDeleteView.as_view(), name="cardapio_delete"),

    # SEMANA
    path("semana/nova/<int:pk>/", SemanaCreateView.as_view(), name="semana_create"),
    path("semana/<int:pk>/editar/", SemanaUpdateView.as_view(), name="semana_update"),
    path("semana/<int:pk>/deletar/", SemanaDeleteView.as_view(), name="semana_delete"),

    # DIA
    path("dia/novo/<int:pk>/", DiaCreateView.as_view(), name="dia_create"),
    path("dia/<int:pk>/editar/", DiaUpdateView.as_view(), name="dia_update"),
    path("dia/<int:pk>/deletar/", DiaDeleteView.as_view(), name="dia_delete"),

    # TIPO REFEICAO
    path("tipo-refeicao/", TipoRefeicaoListView.as_view(), name="tipo_refeicao_list"),
    path("tipo-refeicao/novo/", TipoRefeicaoCreateView.as_view(), name="tipo_refeicao_create"),
    path("tipo-refeicao/<int:pk>/editar/", TipoRefeicaoUpdateView.as_view(), name="tipo_refeicao_update"),
    path("tipo-refeicao/<int:pk>/deletar/", TipoRefeicaoDeleteView.as_view(), name="tipo_refeicao_delete"),

    # ITEM
    path("item/novo/<int:pk>/", ItemCreateView.as_view(), name="item_create"),
    path("item/<int:pk>/editar/", ItemUpdateView.as_view(), name="item_update"),
    path("item/<int:pk>/deletar/", ItemDeleteView.as_view(), name="item_delete"),

    # CARDAPIO ESCOLA
    path("cardapio-escola/novo/", CardapioEscolaCreateView.as_view(), name="cardapio_escola_create"),
    path("cardapio-escola/<int:pk>/deletar/", CardapioEscolaDeleteView.as_view(), name="cardapio_escola_delete"),

     
    
]