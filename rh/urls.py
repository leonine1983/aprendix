from django.urls import path
from rh import views
app_name = 'RH'

urlpatterns = [
    
    path('', views.Profissao_createView.as_view(), name='Profissao_listaView'),
    path('profissao/create/', views.Profissao_createView.as_view(), name='Profissao_createView'),    
    path('profissao/update/<int:pk>',views.Profissao_updateView.as_view(), name='Profissao_updateView'),    
    path('profissao/delete/<int:pk>',views.Profissao_deleteView.as_view(), name='Profissao_deleteView'),
    # PESSOAS
    path('pessoas/create/',views.Pessoas_createView.as_view(), name='Pessoas_createView'),    
    path('pessoas/update/<int:pk>',views.Pessoas_updateView.as_view(), name='Pessoas_updateView'),    
    path('pessoas/delete/<int:pk>',views.Pessoas_deleteView.as_view(), name='Pessoas_deleteView'),

    # ANO
    path('ano/create/',views.Ano_createView.as_view(), name='Ano_createView'),
    path('ano/update/<int:pk>',views.Ano_updateView.as_view(), name='Ano_updateView'),    
    path('ano/delete/<int:pk>',views.Ano_deleteView.as_view(), name='Ano_deleteView'),

    # ESCOLAS
    path('escola/create/',views.Escola_createView.as_view(), name='Escola_createView'),
    path('escola/update/<int:pk>',views.Escola_updateView.as_view(), name='Escola_updateView'),    
    #path('escola/delete/<int:pk>',views.Ano_deleteView.as_view(), name='Escola_deleteView'),

    # CONTRATOS
    path('contratos/create/',views.Contrato_createView.as_view(), name='Contrato_createView'),       
    path('pessoas/update/<int:pk>',views.Pessoas_updateView.as_view(), name='Contrato_updateView'),    
    path('pessoas/delete/<int:pk>',views.Pessoas_deleteView.as_view(), name='Contrato_deleteView'),
    
    path('pessoas/perfi_contrato/<int:pk>',views.Contrato_detailView.as_view(), name='Contrato_detalheView'),    
    #path('pessoas/perfi_contrato/<int:pk>',views.Contrato_detailView, name='Contrato_detalheView'),

    # TEXTOS DO CONTRATO
    path('contratos/texto/create/',views.Texto_contrato_createView.as_view(), name='Texto_Contrato_createView'),        
    path('pessoas/texto/update/<int:pk>',views.Texto_contrato_updateView.as_view(), name='Texto_Contrato_updateView'),      
    path('pessoas/texto/delete/<int:pk>',views.Pessoas_deleteView.as_view(), name='Texto_Contrato_deleteView'),


    
]
