from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from rh.models import Escola
from ...models import Transferencia

class TransferenciasAbertasEscolaView(LoginRequiredMixin, ListView):
    """
    Exibe todas as transferências enviadas e ainda não recebidas de uma escola.
    """
    model = Transferencia
    template_name = "merendaEscolar/escola/transferencias_abertas.html"
    context_object_name = "transferencias"

    def get_queryset(self):
        escola_id = self.kwargs.get("escola_id")
        return Transferencia.objects.filter(
            escola_destino_id=escola_id,
            status="ENVIADO"
        ).order_by("-criado_em")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola_id = self.kwargs.get("escola_id")
        context["escola"] = Escola.objects.get(pk=escola_id)
        return context