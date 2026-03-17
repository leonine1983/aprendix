# modulo_Merendeiras/urls.py

from django.urls import path
from . import views

app_name = "modulo_merendeiras"

urlpatterns = [

    path("", views.DashboardMerendeiraView.as_view(), name="dashboard_merendeira"),

    path("estoque/", views.EstoqueEscolaListView.as_view(), name="estoque_lista"),

    path("receitas/", views.ReceitaListView.as_view(), name="receita_lista"),
    path("receitas/nova/", views.ReceitaCreateView.as_view(), name="receita_nova"),
    path("receitas/<int:pk>/", views.ReceitaDetailView.as_view(), name="receita_detalhe"),

    path("execucoes/", views.ExecucaoListView.as_view(), name="execucao_lista"),
    path("execucoes/<int:pk>/executar/", views.ExecutarReceitaView.as_view(), name="executar_receita"),


       # 📦 Transferências recebidas
    path(
        "transferencias/escola/",
        views.TransferenciasAbertasListView.as_view(),
        name="transferencias_recebidas"
    ),

    # ▶️ Iniciar conferência
    path(
        "transferencias/<int:pk>/iniciar/",
        views.IniciarConferenciaView.as_view(),
        name="iniciar_conferencia"
    ),

    # 🔍 Tela principal de conferência
    path(
        "transferencias/<int:pk>/conferir/",
        views.ConferirTransferenciaView.as_view(),
        name="conferir_transferencia"
    ),

    # ⚠️ Registrar divergência
    path(
        "transferencias/<int:pk>/divergencia/<int:item_id>/",
        views.RegistrarDivergenciaView.as_view(),
        name="registrar_divergencia"
    ),

    # ✅ Confirmar recebimento
    path(
        "transferencias/<int:pk>/confirmar/",
        views.ConfirmarRecebimentoView.as_view(),
        name="confirmar_recebimento"
    ),
]