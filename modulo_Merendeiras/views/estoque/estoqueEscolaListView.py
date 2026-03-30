from django.views.generic import ListView
from django.db.models import Case, When, Value, CharField
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages

from merendaEscolar.models import EstoqueEscola
from ..baseMerendeiraView import BaseMerendeiraView


class EstoqueEscolaListView(BaseMerendeiraView, ListView):
    model = EstoqueEscola
    template_name = "modulo_merendeiras/estoque/estoque_list.html"
    context_object_name = "estoques"
    paginate_by = 20

    def get_queryset(self):
        """
        🔥 Query otimizada com regras institucionais:
        - Filtra por escola
        - Permite filtros dinâmicos
        - Classifica risco (validade)
        """

        escola = self.get_escola_usuario()
        hoje = timezone.now().date()
        alerta = hoje + timedelta(days=30)       


        qs = (
            EstoqueEscola.objects
            .select_related("produto")
            .filter(
                escola=escola,
                quantidade__gt=0  # 🔥 REGRA CRÍTICA
            )
            .annotate(
                status_validade=Case(
                    When(data_validade__lt=hoje, then=Value("vencido")),
                    When(data_validade__lte=alerta, then=Value("alerta")),
                    default=Value("ok"),
                    output_field=CharField()
                )
            )
        )

        # 🔎 FILTROS

        produto = self.request.GET.get("produto")
        if produto:
            qs = qs.filter(produto__nome__icontains=produto)

        ano = self.request.GET.get("ano")
        if ano:
            qs = qs.filter(data_validade__year=ano)

        tipo_status = self.request.GET.get("status")
        if tipo_status:
            if tipo_status == "vencido":
                qs = qs.filter(data_validade__lt=hoje)
            elif tipo_status == "alerta":
                qs = qs.filter(data_validade__range=(hoje, alerta))
            elif tipo_status == "ok":
                qs = qs.filter(data_validade__gt=alerta)

        # 🔥 ordenação inteligente (FEFO visual)
        return qs.order_by("data_validade")

    def get(self, request, *args, **kwargs):
        messages.info(request, "Estoque carregado com sucesso.")
        return super().get(request, *args, **kwargs)