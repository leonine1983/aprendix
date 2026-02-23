from django.views.generic import DetailView
from ...models import Transferencia
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

class TransferenciaDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DetailView
):
    model = Transferencia
    template_name = "merendaEscolar/transferencia/transferencia_detail.html"
    context_object_name = "transferencia"
    permission_required = "merendaEscolar.view_transferencia"