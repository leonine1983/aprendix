from django.views.generic import DetailView
from merendaEscolar.models import Receita
from core.groups.merenda import MerendeirasRequiredMixin
from ..baseMerendeiraView import BaseMerendeiraView


class ReceitaDetailView(MerendeirasRequiredMixin, BaseMerendeiraView, DetailView):
    model = Receita
    template_name = "modulo_merendeiras/cadapioHoje/receita_detail.html"
    context_object_name = "receita"