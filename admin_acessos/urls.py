from django.urls import path
from .views import Faz_logout, Create_Login, Painel_Acesso, Mensagem_create, Mensagem_delete, Mensagem_lista, DetalheView_mensage, UpdateMessageView   
from .views import (
    PaletaCoresListView,
    PaletaCoresDetailView,
    PaletaCoresCreateView,
    PaletaCoresUpdateView,
    PaletaCoresDeleteView,
)

app_name = 'admin_acessos'

urlpatterns = [
    path('create', Faz_logout.as_view(), name='logout' ),
    path('', Create_Login.as_view(), name='login_create' ),
    path('accounts/profile/', Painel_Acesso.as_view(), name='painel_acesso' ),    
    path('accounts/mensagem/', Mensagem_create.as_view(), name='mensagem' ),      
    path('accounts/mensagem/<int:pk>', Mensagem_delete.as_view(), name='mensagem_delete' ),    
    path('accounts/mensagem/lista_enviadas', Mensagem_lista.as_view(), name='mensagem_lista' ),    
    path('accounts/mensagem/update/<int:pk>', UpdateMessageView.as_view(), name='mensagem_update' ),
    path('accounts/mensagem/detalhe/<int:pk>', DetalheView_mensage.as_view(), name='mensagem_detalhe' ),

    path('paletas', PaletaCoresListView.as_view(), name='paletacores_list'),
    path('paleta/<int:pk>/', PaletaCoresDetailView.as_view(), name='paletacores_detail'),
    path('paleta/nova/', PaletaCoresCreateView.as_view(), name='paletacores_create'),
    path('paleta/<int:pk>/editar/', PaletaCoresUpdateView.as_view(), name='paletacores_update'),
    path('paleta/<int:pk>/deletar/', PaletaCoresDeleteView.as_view(), name='paletacores_delete'),
]

