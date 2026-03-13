from django.views.generic import TemplateView
from django.db.models import Sum, Count, Case, When, IntegerField, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta

from merendaEscolar.models import EstoqueCentral, Produto, CategoriaProduto


class RelatorioEstoqueCentralView(TemplateView):
    template_name = "merendaEscolar/relatorios/rel_estoque_central.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hoje = timezone.now().date()

        queryset = EstoqueCentral.objects.select_related(
            "produto",
            "produto__categoria"
        )

        # filtros
        ano = self.request.GET.get("ano")
        mes = self.request.GET.get("mes")
        produto = self.request.GET.get("produto")
        categoria = self.request.GET.get("categoria")

        if ano:
            queryset = queryset.filter(atualizado_em__year=ano)

        if mes:
            queryset = queryset.filter(atualizado_em__month=mes)

        if produto:
            queryset = queryset.filter(produto_id=produto)

        if categoria:
            queryset = queryset.filter(produto__categoria_id=categoria)

        # KPIs
        kpis = queryset.aggregate(

            total_lotes=Count("id"),

            quantidade_total=Coalesce(
                Sum("quantidade"),
                0,
                output_field=DecimalField()
            ),

            vencidos=Count(
                Case(
                    When(data_validade__lt=hoje, then=1),
                    output_field=IntegerField(),
                )
            ),

            criticos=Count(
                Case(
                    When(
                        data_validade__gte=hoje,
                        data_validade__lte=hoje + timedelta(days=7),
                        then=1
                    ),
                    output_field=IntegerField(),
                )
            ),

            alerta=Count(
                Case(
                    When(
                        data_validade__gt=hoje + timedelta(days=7),
                        data_validade__lte=hoje + timedelta(days=30),
                        then=1
                    ),
                    output_field=IntegerField(),
                )
            ),
        )

        # relatório por produto
        produtos = (
            queryset
            .values(
                "produto__id",
                "produto__nome"
            )
            .annotate(

                quantidade_total=Coalesce(
                    Sum("quantidade"),
                    0,
                    output_field=DecimalField()
                ),

                lotes=Count("id")

            )
            .order_by("-quantidade_total", "produto__nome")
        )

        context.update({

            "kpis": kpis,

            "produtos": produtos,

            "anos": range(2023, timezone.now().year + 1),

            "meses": [
                (1, "Janeiro"),
                (2, "Fevereiro"),
                (3, "Março"),
                (4, "Abril"),
                (5, "Maio"),
                (6, "Junho"),
                (7, "Julho"),
                (8, "Agosto"),
                (9, "Setembro"),
                (10, "Outubro"),
                (11, "Novembro"),
                (12, "Dezembro"),
            ],

            "categorias": CategoriaProduto.objects.order_by("nome"),

            "produtos_filtro": Produto.objects.order_by("nome"),

            "filtros": {
                "ano": ano,
                "mes": mes,
                "produto": produto,
                "categoria": categoria,
            }

        })

        return context