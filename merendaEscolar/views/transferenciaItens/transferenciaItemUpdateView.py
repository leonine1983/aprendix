from django.views.generic import UpdateView
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from core.permissions import GroupRequiredMixin
from core.groups.nutricionista import NUTRICIONISTA_GROUPS

from ...models import TransferenciaItem


class TransferenciaItemUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    GroupRequiredMixin,
    UpdateView
):
    model = TransferenciaItem
    fields = ["produto", "estoque_origem", "quantidade"]
    template_name = "merendaEscolar/transferencia/transferenciaitem_form.html"
    permission_required = "merendaEscolar.change_transferenciaitem"
    group_required = NUTRICIONISTA_GROUPS

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj.transferencia.status != "RASCUNHO":
            messages.error(
                request,
                "Itens só podem ser editados enquanto a transferência estiver em rascunho."
            )
            return redirect(
                "merendaEscolar:transferencia-detail",
                pk=obj.transferencia.pk
            )

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(
            self.request,
            "Item atualizado com sucesso."
        )
        return reverse(
            "merendaEscolar:transferencia-detail",
            kwargs={"pk": self.object.transferencia.pk}
        )