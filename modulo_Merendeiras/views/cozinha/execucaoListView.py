from django.views.generic import ListView
from django.db.models import Count, Sum, Q
from django.contrib import messages


from ..baseMerendeiraView import BaseMerendeiraView
from ...models import ExecucaoReceitaCozinha


class ExecucaoListView( BaseMerendeiraView, ListView):
    model = ExecucaoReceitaCozinha
    template_name = "modulo_merendeiras/cozinha/lista_execucoes.html"
    context_object_name = "execucoes"
    paginate_by = 10

    


    def get_queryset(self):
        """
        🔐 Segurança + Performance:
        - Filtra por escola (multi-tenant)
        - Usa annotate() para evitar loops Python
        """
        escola = self.get_escola_usuario()

        if not escola:
            messages.error(self.request, "Usuário não vinculado a uma escola.")
            return ExecucaoReceitaCozinha.objects.none()

        queryset = (
            ExecucaoReceitaCozinha.objects
            .filter(escola=escola)
            .select_related("receita", "iniciado_por", "finalizado_por")
            .annotate(
                total_movimentacoes=Count("movimentacoes", distinct=True),
                total_retirado=Sum(
                    "movimentacoes__quantidade",
                    filter=Q(movimentacoes__tipo="RETIRADA_RECEITA")
                ),
                total_devolvido=Sum(
                    "movimentacoes__quantidade",
                    filter=Q(movimentacoes__tipo="DEVOLUCAO")
                )
            )
            .order_by("-iniciado_em")
        )

        # annotate evita loop Python → escalável e performático
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not context["execucoes"]:
            messages.info(
                self.request,
                "Nenhuma execução de receita encontrada para sua escola."
            )

        return context