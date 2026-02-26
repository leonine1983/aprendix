from django.views.generic import TemplateView
from django.db.models import Sum, F, Case, When, Value, BooleanField
from rh.models import Escola
from ...models import EstoqueEscola


class EstoqueEscolaDashboardView(TemplateView):
    template_name = "merendaEscolar/escola/estoque_escola_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        escola_id = self.kwargs.get("escola_id")
        escola = Escola.objects.get(pk=escola_id)

        estoque = (
            EstoqueEscola.objects
            .filter(escola=escola)
            .values(
                "produto__nome",
                "produto__estoque_minimo",
                "produto__unidade_medida__sigla"
            )
            .annotate(
                total=Sum("quantidade")
            )
            .annotate(
                abaixo_minimo=Case(
                    When(total__lt=F("produto__estoque_minimo"), then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            )
            .order_by("produto__nome")
        )

        # KPIs reais
        total_produtos = estoque.count()
        produtos_criticos = sum(1 for i in estoque if i["abaixo_minimo"])
        produtos_regulares = total_produtos - produtos_criticos

        context.update({
            "escola": escola,
            "estoque": estoque,
            "total_produtos": total_produtos,
            "produtos_criticos": produtos_criticos,
            "produtos_regulares": produtos_regulares,
        })

        return context