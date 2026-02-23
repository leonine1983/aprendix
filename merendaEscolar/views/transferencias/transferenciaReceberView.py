from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse
from ...models import Transferencia

class TransferenciaReceberView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    View,
):
    """
    Confirma o recebimento da transferência pela escola.

    - Atualiza estoque da escola.
    - Gera movimentações.
    - Finaliza o ciclo logístico.
    """

    permission_required = "merendaEscolar.change_transferencia"

    def post(self, request, pk):

        transferencia = get_object_or_404(Transferencia, pk=pk)

        try:
            transferencia.receber(usuario=request.user)
            messages.success(
                request,
                f"Transferência {transferencia.numero} recebida com sucesso."
            )

        except ValidationError as e:
            messages.error(request, e.message)

        except Exception:
            messages.error(
                request,
                "Erro inesperado ao receber a transferência."
            )

        return redirect(reverse("merendaEscolar:transferencia-detail", args=[pk]))