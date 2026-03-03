# modulo_Merendeiras/views.py

from django.views.generic import TemplateView, ListView, DetailView, CreateView, View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Sum
from .forms import ReceitaForm
from merendaEscolar.models import (
    Receita,
    ExecucaoReceita,
    EstoqueEscola,
)
from merendaEscolar.services import executar_receita
from core.permissions import GroupRequiredMixin
from core.groups.merenda import MERENDEIRA_GROUPS


class BaseMerendeiraView(GroupRequiredMixin):
    group_required = MERENDEIRA_GROUPS


# =========================
# DASHBOARD OPERACIONAL
# =========================

class DashboardMerendeiraView(BaseMerendeiraView, TemplateView):
    template_name = "modulo_merendeiras/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        escola = self.request.user.escola

        ctx["total_itens"] = (
            EstoqueEscola.objects
            .filter(escola=escola)
            .aggregate(total=Sum("quantidade"))["total"] or 0
        )

        ctx["receitas_ativas"] = Receita.objects.filter(ativa=True).count()

        ctx["execucoes_hoje"] = ExecucaoReceita.objects.filter(
            escola=escola
        ).count()

        return ctx


# =========================
# ESTOQUE DA ESCOLA
# =========================

class EstoqueEscolaListView(BaseMerendeiraView, ListView):
    model = EstoqueEscola
    template_name = "modulo_merendeiras/estoque_lista.html"
    context_object_name = "estoques"

    def get_queryset(self):
        return (
            EstoqueEscola.objects
            .filter(escola=self.request.user.escola)
            .select_related("produto")
            .order_by("produto__nome")
        )


# =========================
# RECEITAS
# =========================

class ReceitaListView(BaseMerendeiraView, ListView):
    model = Receita
    template_name = "modulo_merendeiras/receita_lista.html"
    context_object_name = "receitas"

    def get_queryset(self):
        return Receita.objects.filter(ativa=True)


class ReceitaCreateView(BaseMerendeiraView, CreateView):
    model = Receita
    form_class = ReceitaForm
    template_name = "modulo_merendeiras/receita_form.html"
    success_url = reverse_lazy("modulo_merendeiras:receita_lista")

    def form_valid(self, form):
        form.instance.criada_por = self.request.user
        messages.success(self.request, "Receita cadastrada com sucesso.")
        return super().form_valid(form)


class ReceitaDetailView(BaseMerendeiraView, DetailView):
    model = Receita
    template_name = "modulo_merendeiras/receita_detalhe.html"


# =========================
# EXECUÇÃO DE RECEITA
# =========================

class ExecucaoListView(BaseMerendeiraView, ListView):
    model = ExecucaoReceita
    template_name = "modulo_merendeiras/execucao_lista.html"
    context_object_name = "execucoes"

    def get_queryset(self):
        return ExecucaoReceita.objects.filter(
            escola=self.request.user.escola
        )


class ExecutarReceitaView(BaseMerendeiraView, View):

    def post(self, request, pk):
        execucao = get_object_or_404(
            ExecucaoReceita,
            pk=pk,
            escola=request.user.escola
        )

        try:
            executar_receita(execucao, request.user)
            messages.success(request, "Receita executada e estoque atualizado.")
        except Exception as e:
            messages.error(request, str(e))

        return redirect("modulo_merendeiras:execucao_lista")