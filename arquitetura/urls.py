# arquitetura/urls.py

from django.urls import path
from .views import Grafo3DView, AtualizarGrafoView

app_name = 'arquitetura_system'

urlpatterns = [
    path("grafo-3d/", Grafo3DView.as_view(), name="grafo_3d"),
    path("atualizar-grafo/", AtualizarGrafoView.as_view(), name="atualizar_grafo"),
]