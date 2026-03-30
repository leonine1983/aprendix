from django.views.generic import CreateView, DetailView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy

from core.permissions import GroupRequiredMixin
from core.groups.merenda import MERENDEIRA_GROUPS
from ..baseMerendeiraView import BaseMerendeiraView

from ...models import ExecucaoReceitaCozinha


class AbrirExecucaoReceitaView(GroupRequiredMixin, CreateView):
    model = ExecucaoReceitaCozinha
    fields = ["receita"]
    template_name = "cozinha/abrir_execucao.html"
    success_url = reverse_lazy("cozinha:lista_execucoes")

    group_required = MERENDEIRA_GROUPS

    def form_valid(self, form):
        form.instance.escola = self.request.user.escola
        form.instance.iniciado_por = self.request.user

        messages.success(self.request, "Receita iniciada com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Erro ao iniciar receita.")
        return super().form_invalid(form)
    
    from django.views.generic import DetailView
from django.db.models import Sum

from ...models import ExecucaoReceitaCozinha, MovimentacaoCozinha
from merendaEscolar.models import EstoqueEscola

from django.contrib import messages
from django.db.models import Sum
from django.views.generic import DetailView

from django.contrib import messages
from django.db.models import Sum
from django.http import Http404
from django.views.generic import DetailView

class PainelExecucaoView(BaseMerendeiraView, DetailView):
    model = ExecucaoReceitaCozinha
    template_name = "cozinha/painel_execucao.html"
    context_object_name = "execucao"

    def get_queryset(self):
        """
        🔐 Segurança institucional:
        Garante isolamento por escola (multi-tenant).
        """
        escola = self.get_escola_usuario()

        if not escola:
            messages.error(self.request, "Usuário não vinculado a uma escola.")
            return ExecucaoReceitaCozinha.objects.none()

        return ExecucaoReceitaCozinha.objects.filter(escola=escola)

    def get_object(self, queryset=None):
        """
        🔎 Garante que o objeto pertence à escola do usuário.
        """
        queryset = self.get_queryset()

        pk = self.kwargs.get("pk")
        if not pk:
            messages.error(self.request, "Execução não informada.")
            raise Http404("Execução não informada")

        try:
            return queryset.get(pk=pk)
        except ExecucaoReceitaCozinha.DoesNotExist:
            messages.error(self.request, "Execução não encontrada para sua escola.")
            raise Http404("Execução não encontrada")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        execucao = self.object

        # 🔥 Estoque agregado (alta performance)
        estoque = (
            EstoqueEscola.objects
            .filter(escola=execucao.escola)
            .values("produto__nome")
            .annotate(total=Sum("quantidade"))
        )
        # annotate evita loops Python → escalável

        context["estoque"] = estoque

        # 🔥 Movimentações (rastreabilidade)
        movimentacoes = (
            MovimentacaoCozinha.objects
            .filter(execucao_receita=execucao)
        )

        context["movimentacoes"] = movimentacoes

        # 🔔 Feedback UX institucional
        if not movimentacoes.exists():
            messages.info(
                self.request,
                "Nenhuma movimentação registrada para esta execução ainda."
            )

        return context
    

    
from django.views import View
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

from ...models import ExecucaoReceitaCozinha
from merendaEscolar.models import Produto
"""
from ...models import retirar_ingrediente_receita


class RetirarIngredienteView(GroupRequiredMixin, View):
    group_required = MERENDEIRA_GROUPS

    def post(self, request, pk):
        execucao = get_object_or_404(ExecucaoReceitaCozinha, pk=pk)

        produto_id = request.POST.get("produto")
        quantidade = request.POST.get("quantidade")

        produto = get_object_or_404(Produto, pk=produto_id)

        try:
            retirar_ingrediente_receita(
                execucao,
                produto,
                float(quantidade),
                request.user
            )

            messages.success(request, "Ingrediente retirado com sucesso.")

        except Exception as e:
            messages.error(request, str(e))

        return redirect("cozinha:painel_execucao", pk=pk)
    """

from ...models import devolver_ingrediente
class DevolverIngredienteView(GroupRequiredMixin, View):
    group_required = MERENDEIRA_GROUPS

    def post(self, request, pk):
        execucao = get_object_or_404(ExecucaoReceitaCozinha, pk=pk)

        try:
            devolver_ingrediente(
                execucao=execucao,
                produto_id=request.POST.get("produto"),
                lote=request.POST.get("lote"),
                quantidade=float(request.POST.get("quantidade")),
                usuario=request.user
            )

            messages.success(request, "Devolução realizada com sucesso.")

        except Exception as e:
            messages.error(request, str(e))

        return redirect("cozinha:painel_execucao", pk=pk)
    

from django.utils import timezone
class FinalizarExecucaoView(GroupRequiredMixin, View):
    group_required = MERENDEIRA_GROUPS

    def post(self, request, pk):
        execucao = get_object_or_404(ExecucaoReceitaCozinha, pk=pk)

        if execucao.status == "FINALIZADA":
            messages.warning(request, "Receita já finalizada.")
            return redirect("cozinha:painel_execucao", pk=pk)

        execucao.status = "FINALIZADA"
        execucao.finalizado_em = timezone.now()
        execucao.save()

        messages.success(request, "Receita finalizada com sucesso.")

        return redirect("cozinha:lista_execucoes")