from django.views.generic import ListView
from django.contrib import messages
from django.db.models import Q

from core.views.baseMerendeira import BaseMerendeiraView
from merendaEscolar.models import MovimentacaoEstoque


class MovimentacaoEstoqueListView(BaseMerendeiraView, ListView):
    model = MovimentacaoEstoque
    template_name = "modulo_merendeiras/movimentaEstoque/movimentacao_list.html"
    context_object_name = "movimentacoes"

    # ==========================================================
    # PAGINAÇÃO DINÂMICA
    # ==========================================================
    def get_paginate_by(self, queryset):
        """
        Usa o valor configurado em:
        ConfiguraPessoal.pagina_movimentacaoEstoque
        """
        if hasattr(self.request.user, "configuracao_pessoal"):
            return (
                self.request.user.configuracao_pessoal.pagina_movimentacaoEstoque
                or 5
            )
        return 5

    # ==========================================================
    # QUERYSET COM FILTROS
    # ==========================================================
    def get_queryset(self):
        escola = self.escola_usuario

        if not escola:
            return MovimentacaoEstoque.objects.none()

        queryset = (
            MovimentacaoEstoque.objects
            .select_related("produto", "usuario", "escola")
            .filter(
                escola=escola,
                tipo__in=["ENTRADA_ESCOLA", "SAIDA_ESCOLA"],
            )
        )

        # --------------------------------------
        # FILTRO POR TEXTO (produto, observação, usuário)
        # --------------------------------------
        q = self.request.GET.get("q", "").strip()
        if q:
            queryset = queryset.filter(
                Q(produto__nome__icontains=q) |
                Q(observacao__icontains=q) |
                Q(usuario__username__icontains=q) |
                Q(usuario__first_name__icontains=q) |
                Q(usuario__last_name__icontains=q)
            )

        # --------------------------------------
        # FILTRO POR TIPO
        # entrada | saida
        # --------------------------------------
        tipo = self.request.GET.get("tipo", "").strip()

        if tipo == "entrada":
            queryset = queryset.filter(tipo="ENTRADA_ESCOLA")

        elif tipo == "saida":
            queryset = queryset.filter(tipo="SAIDA_ESCOLA")

        # --------------------------------------
        # FILTRO POR DATA INICIAL
        # --------------------------------------
        data_inicio = self.request.GET.get("data_inicio", "").strip()
        if data_inicio:
            queryset = queryset.filter(
                data_movimentacao__date__gte=data_inicio
            )

        # --------------------------------------
        # FILTRO POR DATA FINAL
        # --------------------------------------
        data_fim = self.request.GET.get("data_fim", "").strip()
        if data_fim:
            queryset = queryset.filter(
                data_movimentacao__date__lte=data_fim
            )

        return queryset.order_by("-data_movimentacao")

    # ==========================================================
    # CONTEXTO
    # ==========================================================
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Preserva filtros no template
        context["q"] = self.request.GET.get("q", "")
        context["tipo_filtro"] = self.request.GET.get("tipo", "")
        context["data_inicio"] = self.request.GET.get("data_inicio", "")
        context["data_fim"] = self.request.GET.get("data_fim", "")

        # Quantidade configurada pelo usuário
        if hasattr(self.request.user, "configuracao_pessoal"):
            context["itens_por_pagina"] = (
                self.request.user.configuracao_pessoal.pagina_movimentacaoEstoque
                or 5
            )
        else:
            context["itens_por_pagina"] = 5

        # Processa movimentações
        for movimentacao in context["movimentacoes"]:

            # Entrada ou saída
            movimentacao.is_entrada = (
                movimentacao.tipo == "ENTRADA_ESCOLA"
            )

            movimentacao.sinal = (
                "+" if movimentacao.is_entrada else "−"
            )

            movimentacao.classe_tipo = (
                "entrada" if movimentacao.is_entrada else "saida"
            )

            # Responsável padrão
            usuario_responsavel = movimentacao.usuario

            # Para ENTRADA, tenta identificar o nutricionista
            if movimentacao.tipo == "ENTRADA_ESCOLA":
                observacao = movimentacao.observacao or ""

                if "Transferência" in observacao:
                    import re
                    from merendaEscolar.models import Transferencia

                    match = re.search(
                        r"(TRF-\d{4}-\d+)",
                        observacao
                    )

                    if match:
                        numero_transferencia = match.group(1)

                        transferencia = (
                            Transferencia.objects
                            .select_related("enviado_por")
                            .filter(numero=numero_transferencia)
                            .first()
                        )

                        if transferencia and transferencia.enviado_por:
                            usuario_responsavel = (
                                transferencia.enviado_por
                            )

            movimentacao.usuario_responsavel = usuario_responsavel

        # Querystring sem page (para paginação)
        querydict = self.request.GET.copy()
        querydict.pop("page", None)
        context["querystring"] = querydict.urlencode()

        return context

    # ==========================================================
    # GET
    # ==========================================================
    def get(self, request, *args, **kwargs):
        messages.info(
            request,
            "Listagem de movimentações de estoque carregada."
        )
        return super().get(request, *args, **kwargs)