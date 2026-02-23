from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from ...models import Transferencia


class TransferenciaCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CreateView
):
    model = Transferencia
    fields = ["escola_destino"]
    template_name = "merendaEscolar/transferencia/transferencia_form.html"
    permission_required = "merendaEscolar.add_transferencia"

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "merendaEscolar:transferencia-detail",
            kwargs={"pk": self.object.pk}
        )