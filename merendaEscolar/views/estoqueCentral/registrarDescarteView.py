from decimal import Decimal, InvalidOperation

from django.views import View
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin

from ...models import EstoqueCentral, DescarteEstoque, MovimentacaoEstoque


class RegistrarDescarteView(LoginRequiredMixin, View):

    template_name = "merendaEscolar/estoque/descarte_registrar.html"

    def get(self, request, pk):
        """
        Exibe tela institucional de confirmação do descarte.
        """

        estoque = get_object_or_404(EstoqueCentral, pk=pk)

        context = {
            "estoque": estoque,
            "produto": estoque.produto,
        }

        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request, pk):
        """
        Executa o registro sanitário do descarte.
        """

        estoque = get_object_or_404(EstoqueCentral, pk=pk)

        motivo = request.POST.get("motivo")
        descricao = request.POST.get("descricao")
        quantidade = request.POST.get("quantidade")

        if not motivo:
            messages.error(request, "Informe o motivo do descarte.")
            return redirect("merendaEscolar:registrar-descarte", pk=pk)

        # conversão segura para Decimal
        try:
            quantidade = Decimal(quantidade)
        except (InvalidOperation, TypeError):
            messages.error(request, "Quantidade inválida.")
            return redirect("merendaEscolar:registrar-descarte", pk=pk)

        if quantidade <= 0:
            messages.error(request, "Quantidade deve ser maior que zero.")
            return redirect("merendaEscolar:registrar-descarte", pk=pk)

        if quantidade > estoque.quantidade:
            messages.error(request, "Quantidade maior que o saldo disponível.")
            return redirect("merendaEscolar:registrar-descarte", pk=pk)


        # registro sanitário do descarte
        descarte = DescarteEstoque.objects.create(
            estoque=estoque,
            produto=estoque.produto,
            quantidade=quantidade,
            motivo=motivo,
            descricao=descricao,
            registrado_por=request.user
        )

        # movimentação auditável
        MovimentacaoEstoque.objects.create(
            produto=estoque.produto,
            quantidade=quantidade,
            tipo="AJUSTE",
            usuario=request.user,
            observacao=f"Descarte sanitário do lote {estoque.lote} - Motivo: {motivo}"
        )

        # baixa no estoque
        estoque.quantidade -= quantidade
        estoque.save(update_fields=["quantidade"])

        messages.warning(
            request,
            f"Descarte registrado para o produto {estoque.produto.nome}."
        )

        return redirect(
            reverse("merendaEscolar:nota-descarte", args=[descarte.id])
        )