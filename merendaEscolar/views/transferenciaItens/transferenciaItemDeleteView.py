from django.views.generic import DeleteView
from django.urls import reverse
from django.shortcuts import redirect

from django.contrib import messages
from django.core.exceptions import ValidationError

from core.permissions import GroupRequiredMixin
from core.groups.nutricionista import NUTRICIONISTA_GROUPS
from ...models import TransferenciaItem
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class TransferenciaItemDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    GroupRequiredMixin,
    DeleteView
):
    model = TransferenciaItem
    template_name = "merendaEscolar/transferencia/transferenciaitem_confirm_delete.html"
    permission_required = "merendaEscolar.delete_transferenciaitem"
    group_required = NUTRICIONISTA_GROUPS

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj.transferencia.status != "RASCUNHO":
            messages.error(
                request,
                "Não é permitido excluir itens de transferência já enviada."
            )
            return redirect(
                "merendaEscolar:transferencia-detail",
                pk=obj.transferencia.pk
            )

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(
            self.request,
            "Item removido da transferência com sucesso."
        )
        return reverse(
            "merendaEscolar:transferencia-detail",
            kwargs={"pk": self.object.transferencia.pk}
        )