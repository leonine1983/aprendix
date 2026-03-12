from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from ...models import DescarteEstoque


class NotaDescarteView(LoginRequiredMixin, DetailView):
    """
    Comprovante institucional de descarte sanitário.
    Utilizado para auditoria, controle nutricional e impressão.
    """

    model = DescarteEstoque
    template_name = "merendaEscolar/estoque/nota_descarte.html"
    context_object_name = "descarte"

    def get(self, request, *args, **kwargs):

        messages.info(
            request,
            "Comprovante de descarte gerado. Caso necessário, realize a impressão para arquivo físico."
        )

        return super().get(request, *args, **kwargs)