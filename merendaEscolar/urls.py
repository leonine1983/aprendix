from django.urls import path, include
from . views import *



app_name = 'merendaEscolar'
urlpatterns = [    
    path('', inicio_merenda, name='merenda_inicio'),  
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


    
    
]