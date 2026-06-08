from django.urls import path
from .views import *

app_name = 'atividadePedagogica'

urlpatterns = [
    
    path('area_pedagogica/', atividadePedagogicaView, name='inicio'),
    path(
        "jogos/novo/",
        JogoPedagogicoCreateView.as_view(),
        name="jogo_create"
    ),

]