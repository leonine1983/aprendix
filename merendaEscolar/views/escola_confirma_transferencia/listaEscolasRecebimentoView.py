from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from rh.models import Escola
from ...models import Transferencia
from core.views.baseNutricionista import BaseNutricionistaView

class ListaEscolasRecebimentoView(BaseNutricionistaView, ListView):
    """
    Exibe todas as escolas para que o usuário selecione qual deseja receber transferências.
    """
    model = Escola
    template_name = "merendaEscolar/escola/lista_escolas_recebimento.html"
    context_object_name = "escolas"
    ordering = ["nome_escola"] 