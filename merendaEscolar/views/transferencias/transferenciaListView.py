from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from ...models import Transferencia

from core.permissions import GroupRequiredMixin
from core.groups.nutricionista import NUTRICIONISTA_GROUPS
from django.core.exceptions import PermissionDenied

class TransferenciaListView(
    LoginRequiredMixin,
    GroupRequiredMixin,
    PermissionRequiredMixin,
    ListView
):
    model = Transferencia
    template_name = "merendaEscolar/transferencia/transferencia_list.html"
    context_object_name = "transferencias"
    paginate_by = 4
    
    group_required = NUTRICIONISTA_GROUPS
    permission_required = "merendaEscolar.view_estoquecentral"

    permission_required = "merendaEscolar.view_transferencia"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("escola_destino", "criado_por")
        )