from django.views.generic import ListView
from rh.models import Escola

class ListaEscolasView(ListView):
    model = Escola
    template_name = "merendaEscolar/escola/escolas_list.html"
    context_object_name = "escolas"
    ordering = ["nome_escola"]

    # UX institucional: permitir busca rápida por nome
    def get_queryset(self):
        qs = super().get_queryset()
        termo = self.request.GET.get("q")
        if termo:
            qs = qs.filter(nome_escola__icontains=termo)
        return qs