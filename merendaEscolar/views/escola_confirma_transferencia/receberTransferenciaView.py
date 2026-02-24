from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.views import View
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin
from ...models import Transferencia, TransferenciaItem

class ReceberTransferenciaView(LoginRequiredMixin, View):
    """
    View que permite à escola confirmar o recebimento de uma transferência enviada.
    """

    template_name = "merendaEscolar/escola/receber_transferencia.html"

    def get(self, request, pk):
        transferencia = get_object_or_404(Transferencia, pk=pk)
        if transferencia.status != "ENVIADO":
            messages.warning(request, "Somente transferências enviadas podem ser recebidas.")
            return redirect('merendaEscolar:lista')
        itens = transferencia.itens.all()
        return render(request, self.template_name, {"transferencia": transferencia, "itens": itens})

    def post(self, request, pk):
        transferencia = get_object_or_404(Transferencia, pk=pk)
        try:
            transferencia.receber(usuario=request.user)
            messages.success(request, f"Transferência {transferencia.numero} recebida com sucesso.")
            return redirect('merendaEscolar:lista_escolas')
        except ValidationError as e:
            messages.error(request, e.message)
            return redirect('merendaEscolar:escola_receber', pk=pk)