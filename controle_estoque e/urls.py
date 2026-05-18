from django.urls import path
from controle_estoque import views


app_name = 'controle_estoque'

urlpatterns = [
    path('', views.index, name='index'),
    path('informacoes_sobre_o_sistema', views.sobre_system, name='about'),
    # Prefeitura
    path('prefeitura/perfil', views.prefeitura.Prefeitura_View.as_view(), name='prefeitura_view'),    
    path('prefeitura/perfil/create/', views.prefeitura.Prefeitura_Create.as_view(), name='prefeitura_create'),
    path('prefeitura/perfil/update/<int:pk>', views.prefeitura.Prefeitura_Update.as_view(), name='prefeitura_update'),
    # ESCOLAS
    path('escolas/create', views.Escolas_CreateView.as_view(), name='escolas_view'),    
    path('escolas/update/<int:pk>', views.Escolas_updateView.as_view(), name='escolas_update'),
    path('escolas/lista', views.Escolas_ListView.as_view(), name='escolas_lista'),  
    path('escolas/delete/<int:pk>', views.Escolas_DeleteView.as_view(), name='escolas_delete'),

    # CATEGORIA / alimentos    
    path('categoria/lista', views.alimentos.Categoria_ListView.as_view(), name='categoria_lista'),
    path('categoria/create', views.alimentos.Categoria_CreateView.as_view(), name='categoria_view'),    
    path('categoria/update/<int:pk>', views.alimentos.Categoria_UpdateView.as_view(), name='categoria_update'),
    path('categoria/delete/<int:pk>', views.Escolas_DeleteView.as_view(), name='categoria_delete'),
    # ALIMENTOS
    path('alimentos/create', views.alimentos.Alimento_CreateView.as_view(), name='alimento_view'),    
    path('alimentos/update/<int:pk>', views.alimentos.Alimentos_UpdateView.as_view(), name='alimentos_update'),
    path('alimentos/lista', views.alimentos.Alimentos_ListView.as_view(), name='alimento_lista'),  
    path('alimentos/delete/<int:pk>', views.alimentos.Alimentos_DeleteView.as_view(), name='alimento_delete'),
    # Fornecedores
    path('fornecedores/lista', views.fornecedores.Fornecedor_ListView.as_view(), name='fornecedor_listaView'),
    path('fornecedores/cadastro', views.fornecedores.Fornecedor_CreateView.as_view(), name='fornecedor_CreateVies'),
    path('fornecedores/delete/<int:pk>', views.fornecedores.Fornecedor_DeleteView.as_view(), name='fornecedor_DeleteViews'),
    path('fornecedores/update/<int:pk>', views.fornecedores.Fornecedor_updateView.as_view(), name='fornecedor_UpdateView'),
    # Movimentação de Estoque
    path('movi_estoque/lista', views.MovimentoEstoque_ListView.as_view(), name='movi_estoque_listaView'),
    path('movi_estoque/cadastro/saida', views.MovimentoEstoque_Saida_CreateView.as_view(), name='movi_estoque_CreateVies'),
    path('movi_estoque/cadastro/entrada', views.MovimentoEstoque_Entrada_CreateView.as_view(), name='movi_estoque_entrada_CreateVies'),
    path('movi_estoque/delete/<int:pk>', views.MovimentoEstoque_DeleteView.as_view(), name='movi_estoque_DeleteViews'),
    path('movi_estoque/update/<int:pk>', views.MovimentoEstoque_updateView.as_view(), name='movi_estoque_UpdateView'),    
    # Programação de Saída de Estoque
    path('program_estoque/lista', views.ProgramaEstoque_ListView.as_view(), name='program_estoque_listaView'),
    path('program_estoque/cadastro', views.ProgramaEstoque_CreateView.as_view(), name='program_estoque_CreateVies'),
    path('program_estoque/delete/<int:pk>', views.ProgramaEstoque_DeleteView.as_view(), name='program_estoque_DeleteViews'),
    path('program_estoque/update/<int:pk>', views.ProgramaEstoque_updateView.as_view(), name='program_estoque_UpdateView'),    
    path('program_estoque/detalhe/<int:pk>', views.ProgramaEstoque_Ver_detailView.as_view(), name='detalhe_UpdateView'), 
]


