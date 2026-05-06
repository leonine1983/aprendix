from django.views.generic import ListView
from django.db.models import Count, Sum, Q
from django.contrib import messages

from core.views.baseMerendeira import BaseMerendeiraView
from ...models import ExecucaoReceitaCozinha, ExecucaoCardapioDia
from django.db.models import OuterRef, Subquery


class ExecucaoListView( BaseMerendeiraView, ListView):
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


    from django.db.models import OuterRef, Subquery

    def get_queryset(self):
        escola = self.get_escola_usuario()

        if not escola:
            messages.error(self.request, "Usuário não vinculado a uma escola.")
            return ExecucaoReceitaCozinha.objects.none()

        execucao_cardapio_subquery = ExecucaoCardapioDia.objects.filter(
            escola=OuterRef("escola"),
            data=OuterRef("iniciado_em__date"),
            cardapio_dia__itens__receita=OuterRef("receita")
        ).values("turno")[:1]

        queryset = (
            ExecucaoReceitaCozinha.objects
            .filter(escola=escola)
            .select_related("receita", "iniciado_por", "finalizado_por")
            .annotate(
                turno=Subquery(execucao_cardapio_subquery),
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

        return queryset
    
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not context["execucoes"]:
            messages.info(
                self.request,
                "Nenhuma execução de receita encontrada para sua escola."
            )

        return context