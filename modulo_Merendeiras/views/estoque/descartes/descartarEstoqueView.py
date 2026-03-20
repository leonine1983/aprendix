from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
import traceback

from merendaEscolar.models import EstoqueEscola
from ....models import descartar_produto_escola
from ...baseMerendeiraView import BaseMerendeiraView


class DescartarEstoqueView(BaseMerendeiraView, View):

    template_name = "modulo_merendeiras/descartes/lista_descartes.html"

    def get(self, request, pk):
        """
        📄 Exibe formulário de descarte
        """

        estoque = get_object_or_404(
            EstoqueEscola,
            pk=pk,
            escola=self.get_escola_usuario()
        )

        return render(request, self.template_name, {
            "estoque": estoque
        })

    def post(self, request, pk):
        """
        💾 Processa descarte com regra institucional
        """

        estoque = get_object_or_404(
            EstoqueEscola,
            pk=pk,
            escola=self.get_escola_usuario()
        )

        # 🔁 Preservação de estado (UX)
        quantidade_valor = request.POST.get("quantidade", "")
        motivo_valor = request.POST.get("motivo", "")
        descricao_valor = request.POST.get("descricao", "")

        try:
            # 🔢 Conversão segura
            try:
                quantidade = Decimal(quantidade_valor)
            except (InvalidOperation, TypeError):
                raise ValidationError("Quantidade inválida.")

            # 🔴 Validações básicas
            if quantidade <= 0:
                raise ValidationError("Quantidade deve ser maior que zero.")

            if not motivo_valor:
                raise ValidationError("Selecione o motivo do descarte.")

            # 🔥 Regra de negócio centralizada
            descartar_produto_escola(
                estoque=estoque,
                quantidade=quantidade,
                motivo=motivo_valor,
                usuario=request.user,
                descricao=descricao_valor
            )

            # ✅ Feedback institucional
            messages.success(
                request,
                f"Descarte registrado com sucesso. Produto: {estoque.produto.nome} | Quantidade: {quantidade}"
            )

            return redirect("modulo_merendeiras:estoque_list_escola")

        except ValidationError as e:
            messages.error(request, str(e))

        except Exception as e:
            # 🔍 DEBUG REAL (agora funciona)
            print("\n=== ERRO REAL NO DESCARTE ===")
            print(str(e))
            traceback.print_exc()
            print("=== FIM ERRO ===\n")

            messages.error(
                request,
                "Erro interno ao registrar descarte. Contate o suporte."
            )

        # 🔁 Retorno com estado preservado
        return render(request, self.template_name, {
            "estoque": estoque,
            "quantidade_valor": quantidade_valor,
            "motivo_valor": motivo_valor,
            "descricao_valor": descricao_valor,
        })