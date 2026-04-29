from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from core.permissions import GroupRequiredMixin
from core.groups.nutricionista import NUTRICIONISTA_GROUPS
from core.views.baseNutricionista import BaseNutricionistaView

from ...models import Transferencia
import traceback


class TransferenciaEnviarView(BaseNutricionistaView, View):
    
    """
    Responsável por executar o envio formal da transferência.

    - Valida permissões.
    - Chama método institucional do model.
    - Garante integridade do fluxo.
    """

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
       
        

        except Exception as e:
            print("ERRO REAL >>>>>>>>>>>>>>>")
            traceback.print_exc()

            messages.error(
                request,
                f"Erro inesperado: {str(e)}"
            )

        #return redirect(reverse("merendaEscolar:transferencia-detail", args=[pk]))
        return redirect(reverse("merendaEscolar:transferencia-print", args=[pk])
)