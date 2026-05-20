class MovimentacaoEstoqueListView(
    LoginRequiredMixin,
    GroupRequiredMixin,
    ListView
):
    """
    Lista apenas as movimentações de estoque da escola da merendeira.

    Regras aplicadas:
    - Considera somente:
        * ENTRADA_ESCOLA
        * SAIDA_ESCOLA
    - Ignora movimentações do depósito central:
        * ENTRADA_CENTRAL
        * SAIDA_CENTRAL
    - Exibe apenas movimentações da escola vinculada ao usuário.
    """

    model = MovimentacaoEstoque
    template_name = "modulo_merendeiras/movimentaEstoque/movimentacao_list.html"
    context_object_name = "movimentacoes"
    paginate_by = 20

    group_required = MERENDEIRA_GROUPS

    def get_queryset(self):
        escola = getattr(self.request.user, "escola", None)

        if not escola:
            return MovimentacaoEstoque.objects.none()

        return (
            MovimentacaoEstoque.objects
            .select_related("produto", "usuario", "escola")
            .filter(
                escola=escola,
                tipo__in=[
                    "ENTRADA_ESCOLA",
                    "SAIDA_ESCOLA",
                ],
            )
            .order_by("-data_movimentacao")
        )

    def get(self, request, *args, **kwargs):
        messages.info(
            request,
            "Listagem de movimentações de estoque da escola carregada."
        )
        return super().get(request, *args, **kwargs)