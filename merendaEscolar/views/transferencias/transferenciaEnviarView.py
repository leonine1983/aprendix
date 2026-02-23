from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse

from ...models import Transferencia


class TransferenciaEnviarView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    View,
):
    """
    Responsável por executar o envio formal da transferência.

    - Valida permissões.
    - Chama método institucional do model.
    - Garante integridade do fluxo.
    """

    permission_required = "merendaEscolar.change_transferencia"

    def post(self, request, pk):

        transferencia = get_object_or_404(Transferencia, pk=pk)

        try:
            transferencia.enviar(usuario=request.user)
            messages.success(
                request,
                f"Transferência {transferencia.numero} enviada com sucesso."
            )

        except ValidationError as e:
            messages.error(request, e.message)

        
        except Exception:
            messages.error(
                request,
                "Erro inesperado ao enviar a transferência."
            )

        return redirect(reverse("merendaEscolar:transferencia-detail", args=[pk]))