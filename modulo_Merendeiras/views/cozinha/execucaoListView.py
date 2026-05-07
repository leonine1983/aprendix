from django.views.generic import ListView
from django.db.models import Count, Sum, Q, Prefetch
from django.contrib import messages

from core.views.baseMerendeira import BaseMerendeiraView
from ...models import ExecucaoCardapioDia, ExecucaoCardapioItem


class ExecucaoListView(BaseMerendeiraView, ListView):
    model = ExecucaoCardapioDia
    template_name = "modulo_merendeiras/cozinha/lista_execucoes.html"
    context_object_name = "execucoes"

    def get_paginate_by(self, queryset):
        return self.configuracao.pagina_ExecutaReceitas or 5

    def post(self, request, *args, **kwargs):
        valor = request.POST.get("pagina_ExecutaReceitas")
        try:
            valor = int(valor)
            if valor > 0:
                self.configuracao.pagina_ExecutaReceitas = valor
                self.configuracao.save()
                messages.success(request, "Paginação atualizada com sucesso!")
        except (TypeError, ValueError):
            messages.error(request, "Valor inválido para paginação.")
        return self.get(request, *args, **kwargs)

    def get_queryset(self):
        escola = self.get_escola_usuario()

        if not escola:
            messages.error(self.request, "Usuário não vinculado a uma escola.")
            return ExecucaoCardapioDia.objects.none()

        return (
            ExecucaoCardapioDia.objects
            .filter(escola=escola)
            .select_related("escola", "executado_por", "cardapio_dia")
            .prefetch_related(
                Prefetch(
                    "itens_executados",
                    queryset=ExecucaoCardapioItem.objects.select_related(
                        "receita", "tipo_refeicao", "execucao_receita"
                    )
                )
            )
            .annotate(
                # Total de itens (receitas) vinculados ao dia
                total_itens=Count("itens_executados", distinct=True),
                # Itens executados com sucesso
                total_executados=Count(
                    "itens_executados",
                    filter=Q(itens_executados__status="EXECUTADO"),
                    distinct=True,
                ),
                # Porções totais produzidas no dia
                total_porcoes=Sum(
                    "itens_executados__porcoes_executadas",
                    filter=Q(itens_executados__status="EXECUTADO"),
                ),
            )
            .order_by("-data", "-criado_em")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not context["execucoes"]:
            messages.info(
                self.request,
                "Nenhuma execução de cardápio encontrada para sua escola."
            )

        context["config"] = self.configuracao
        return context