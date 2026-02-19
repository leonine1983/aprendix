from django.views.generic import FormView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.utils import timezone

from ..models import (
    EstoqueCentral,
    MovimentacaoEstoque,
    Escola,
    DivergenciaEntrega
)
from ..forms import EntradaEstoqueCentralForm


# ===============================
# ENTRADA DE ESTOQUE CENTRAL
# ===============================

class EntradaEstoqueCentralView(LoginRequiredMixin, FormView):
    template_name = "estoque/entrada_central_form.html"
    form_class = EntradaEstoqueCentralForm
    success_url = reverse_lazy("merendaEscolar:entrada-central")  # corrigido namespace

    def form_valid(self, form):
        produto = form.cleaned_data["produto"]
        lote = form.cleaned_data["lote"]
        data_validade = form.cleaned_data["data_validade"]
        quantidade = form.cleaned_data["quantidade"]
        observacao = form.cleaned_data["observacao"]

        with transaction.atomic():

            estoque, created = EstoqueCentral.objects.select_for_update().get_or_create(
                produto=produto,
                lote=lote,
                defaults={
                    "quantidade": 0,
                    "data_validade": data_validade
                }
            )

            estoque.quantidade += quantidade

            if data_validade:
                estoque.data_validade = data_validade

            estoque.save()

            # corrigido: tipo como string (seu model não usa enum)
            MovimentacaoEstoque.objects.create(
                produto=produto,
                quantidade=quantidade,
                tipo="ENTRADA_CENTRAL",
                usuario=self.request.user,
                observacao=observacao
            )

        messages.success(self.request, "Entrada registrada com sucesso no estoque central.")
        return super().form_valid(form)


# ===============================
# DASHBOARD ESTOQUE CENTRAL
# ===============================

class EstoqueCentralListView(LoginRequiredMixin, ListView):
    model = EstoqueCentral
    template_name = "estoque/estoque_central.html"
    context_object_name = "produtos"

    def get_queryset(self):
        return (
            EstoqueCentral.objects
            .select_related("produto")
            .order_by("produto__nome")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hoje = timezone.now().date()
        produtos = context["produtos"]

        # Total consolidado em estoque
        total_itens = produtos.aggregate(
            total=Sum("quantidade")
        )["total"] or 0

        # Escolas atendidas
        escolas_atendidas = Escola.objects.count()

        # Primeiro dia do mês atual
        inicio_mes = hoje.replace(day=1)

        # corrigido: campo correto do model
        envios_mes = MovimentacaoEstoque.objects.filter(
            tipo="SAIDA_CENTRAL",
            data_movimentacao__date__gte=inicio_mes
        ).count()

        # corrigido: sem enum inexistente
        divergencias_abertas = DivergenciaEntrega.objects.filter(
            status="ABERTA"
        ).count()

        context.update({
            "total_itens_estoque": total_itens,
            "escolas_atendidas": escolas_atendidas,
            "envios_mes": envios_mes,
            "divergencias_abertas": divergencias_abertas,
        })

        return context
