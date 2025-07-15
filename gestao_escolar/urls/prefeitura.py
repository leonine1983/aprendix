from django.urls import path
from gestao_escolar.views.GE_pasta_escola import *
from gestao_escolar.views.pasta_session import *
from gestao_escolar.views import *

urlpatterns = [
    # path("", PrefeituraListView.as_view(), name="lista"),
    # path("nova/", PrefeituraCreateView.as_view(), name="nova"),
    # path("<int:pk>/", PrefeituraDetailView.as_view(), name="detalhe"),
    path("<int:pk>/editar/", PrefeituraUpdateView.as_view(), name="PrefeituraEditar"),
    path("<int:pk>/excluir/", PrefeituraDeleteView.as_view(), name="excluir")   
] 


