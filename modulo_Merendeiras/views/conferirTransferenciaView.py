from django.views.generic import DetailView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from merendaEscolar.models import Transferencia
from .views import BaseMerendeiraView  # ajuste se estiver no mesmo arquivo


class ConferirTransferenciaView(BaseMerendeiraView, DetailView):
    model = Transferencia
    template_name = "modulo_merendeiras/conferir_transferencia.html"
    context_object_name = "transferencia"

    def get_queryset(self):
        """
        🔒 Segurança institucional:
        - Garante que a merendeira só acesse transferências da sua escola
        - Garante que só esteja em conferência
        """
        escola = self.get_escola_usuario()

        return (
            Transferencia.objects
            .filter(
                escola_destino=escola,
                status="EM_CONFERENCIA"
            )
            .prefetch_related("divergencias")
        )

    def dispatch(self, request, *args, **kwargs):
        """
        🔐 Camada defensiva:
        Evita acesso indevido via URL direta
        """
        escola = self.get_escola_usuario()

        if not escola:
            messages.error(request, "Usuário sem escola vinculada.")
            return redirect("modulo_merendeiras:transferencias_recebidas")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        transferencia = self.object

        # 🔥 PERFORMANCE:
        # select_related evita N+1 queries nos produtos e lotes
        ctx["itens"] = (
            transferencia.itens
            .select_related("produto", "estoque_origem")
        )

        ctx["divergencias"] = transferencia.divergencias.all()

        # 🔥 UX INTELIGENTE (opcional mas poderoso)
        ctx["total_itens"] = transferencia.itens.count()
        ctx["total_divergencias"] = transferencia.divergencias.count()

        return ctx