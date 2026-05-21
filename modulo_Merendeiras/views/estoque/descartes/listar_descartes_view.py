from django.views import View
from django.shortcuts import render
from django.db.models import F

from ....models import DescarteEstoqueEscola
from core.views.baseMerendeira import BaseMerendeiraView


class ListaDescartesView(BaseMerendeiraView, View):

    template_name = "modulo_merendeiras/descartes/lista_descartes.html"

    def get(self, request):

        escola = self.get_escola_usuario()

        descartes = (
            DescarteEstoqueEscola.objects
            .filter(escola=escola)
            .select_related("produto", "registrado_por")
            .only(
                "produto__nome",
                "quantidade",
                "motivo",
                "registrado_por__username",
                "criado_em",
                "lote"
            )
            .order_by("-criado_em")
        )

        return render(request, self.template_name, {
            "descartes": descartes
        })