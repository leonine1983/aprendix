from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from ...models import Transferencia

class TransferenciaListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    ListView
):
    model = Transferencia
    template_name = "merendaEscolar/transferencia/transferencia_list.html"
    context_object_name = "transferencias"
    paginate_by = 20
    permission_required = "merendaEscolar.view_transferencia"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("escola_destino", "criado_por")
        )