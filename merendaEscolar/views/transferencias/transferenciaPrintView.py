from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from core.permissions import GroupRequiredMixin
from core.groups.nutricionista import NUTRICIONISTA_GROUPS
from ...models import Transferencia


class TransferenciaPrintView(
    LoginRequiredMixin,
    GroupRequiredMixin,
    PermissionRequiredMixin,
    DetailView
):

    model = Transferencia
    template_name = "merendaEscolar/transferencia/transferencia_print.html"
    context_object_name = "transferencia"

    group_required = NUTRICIONISTA_GROUPS
    permission_required = "merendaEscolar.view_transferencia"