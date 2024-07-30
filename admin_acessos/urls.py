from django.urls import path
from .views import LogoutView, CreateLoginView, PainelAcessoView, MensagemCreateView, MensagemDeleteView, MensagemListView, DetalheMensagemView, UpdateMessageView   
from .views import (
    PaletaCoresListView,
    PaletaCoresDetailView,
    PaletaCoresCreateView,
    PaletaCoresUpdateView,
    PaletaCoresDeleteView,
)

app_name = 'admin_acessos'

urlpatterns = [
    path('create', LogoutView.as_view(), name='logout' ),
    path('', CreateLoginView.as_view(), name='login_create' ),
    path('accounts/profile/', PainelAcessoView.as_view(), name='painel_acesso' ),    
    path('accounts/mensagem/', MensagemCreateView.as_view(), name='mensagem' ),      
    path('accounts/mensagem/<int:pk>', MensagemDeleteView.as_view(), name='mensagem_delete' ),    
    path('accounts/mensagem/lista_enviadas', MensagemListView.as_view(), name='mensagem_lista' ),    
    path('accounts/mensagem/update/<int:pk>', UpdateMessageView.as_view(), name='mensagem_update' ),
    path('accounts/mensagem/detalhe/<int:pk>', DetalheMensagemView.as_view(), name='mensagem_detalhe' ),

    path('paletas', PaletaCoresListView.as_view(), name='paletacores_list'),
    path('paleta/<int:pk>/', PaletaCoresDetailView.as_view(), name='paletacores_detail'),
    path('paleta/nova/', PaletaCoresCreateView.as_view(), name='paletacores_create'),
    path('paleta/<int:pk>/editar/', PaletaCoresUpdateView.as_view(), name='paletacores_update'),
    path('paleta/<int:pk>/deletar/', PaletaCoresDeleteView.as_view(), name='paletacores_delete'),
]


