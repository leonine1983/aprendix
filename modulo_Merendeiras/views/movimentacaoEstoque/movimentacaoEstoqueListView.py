from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.db.models import F

from core.views.baseMerendeira import BaseMerendeiraView

from merendaEscolar.models import MovimentacaoEstoque


class MovimentacaoEstoqueListView(BaseMerendeiraView, ListView):
    model = MovimentacaoEstoque
    template_name = "modulo_merendeiras/movimentaEstoque/movimentacao_list.html"
    context_object_name = "movimentacoes"
    paginate_by = 200

    # views.py
    def get_queryset(self):
        escola = self.escola_usuario
        if not escola:
            return MovimentacaoEstoque.objects.none()

        return (
            MovimentacaoEstoque.objects
            .select_related("produto", "usuario", "escola")
            .filter(
                escola=escola,
                tipo__in=["ENTRADA_ESCOLA", "SAIDA_ESCOLA"],
            )
            .order_by("-data_movimentacao")  # ← era criado_em, não existe no model
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Adiciona informações calculadas para cada movimentação
        for movimentacao in context["movimentacoes"]:
            # Entrada = positivo / Saída = negativo
            movimentacao.is_entrada = (
                movimentacao.tipo == "ENTRADA_ESCOLA"
            )

            movimentacao.sinal = "+" if movimentacao.is_entrada else "−"

            movimentacao.classe_tipo = (
                "entrada" if movimentacao.is_entrada else "saida"
            )

            # ==========================================================
            # RESPONSÁVEL REAL DA MOVIMENTAÇÃO
            # ==========================================================
            #
            # ENTRADA_ESCOLA:
            #   Quem registra é a merendeira (usuario),
            #   mas quem efetivamente enviou foi o nutricionista
            #   (Transferencia.enviado_por).
            #
            # SAIDA_ESCOLA:
            #   Quem realizou a saída é a própria merendeira
            #   (usuario).
            # ==========================================================

            usuario_responsavel = movimentacao.usuario

            # Se for entrada, tenta localizar a transferência associada
            if movimentacao.tipo == "ENTRADA_ESCOLA":
                observacao = movimentacao.observacao or ""

                # Ex.: "Recebimento da Transferência TRF-2026-00001"
                if "Transferência" in observacao:
                    import re

                    match = re.search(
                        r"(TRF-\d{4}-\d+)",
                        observacao
                    )

                    if match:
                        numero_transferencia = match.group(1)

                        from merendaEscolar.models import Transferencia

                        transferencia = (
                            Transferencia.objects
                            .select_related("enviado_por")
                            .filter(numero=numero_transferencia)
                            .first()
                        )

                        # Mostra quem enviou (nutricionista)
                        if transferencia and transferencia.enviado_por:
                            usuario_responsavel = (
                                transferencia.enviado_por
                            )

            movimentacao.usuario_responsavel = usuario_responsavel

        return context

    def get(self, request, *args, **kwargs):
        messages.info(
            request,
            "Listagem de movimentações de estoque carregada."
        )
        return super().get(request, *args, **kwargs)