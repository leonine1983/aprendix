from django.views.generic import TemplateView
from django.utils import timezone
from core.groups.merenda import MerendeirasRequiredMixin
from ..baseMerendeiraView import BaseMerendeiraView

from merendaEscolar.models import (
    CardapioEscola,
    CardapioItem,
)


class CardapioHojeView(MerendeirasRequiredMixin, BaseMerendeiraView, TemplateView):
    """
    Exibe o cardápio do dia atual para a merendeira logada.
    """

    template_name = "modulo_merendeiras/cadapioHoje/cardapio_hoje.html"

    # ------------------------------------------------------------------ #
    # Helpers                                                            #
    # ------------------------------------------------------------------ #

    def _calcular_semana(self, data_inicio, hoje):
        delta = (hoje - data_inicio).days
        return (delta // 7) + 1

    # ------------------------------------------------------------------ #
    # Contexto principal                                                 #
    # ------------------------------------------------------------------ #

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hoje = timezone.localdate()
        dia_semana_iso = hoje.isoweekday()  # 1=Segunda … 7=Domingo

        # ── 1. Escola (via BaseMerendeiraView) ─────────────────────────
        escola = self.get_escola_usuario()

        context["escola"] = escola
        context["hoje"] = hoje
        context["dia_semana_iso"] = dia_semana_iso

        # 🚫 Fim de semana
        if dia_semana_iso > 5:
            context["sem_cardapio"] = True
            context["motivo"] = "Hoje é fim de semana. Não há merenda escolar."
            return context

        # 🚫 Usuário sem escola
        if not escola:
            context["sem_cardapio"] = True
            context["motivo"] = "Seu usuário não está vinculado a nenhuma escola."
            return context

        # ── 2. Cardápio ativo ─────────────────────────────────────────
        vinculo = (
            CardapioEscola.objects
            .select_related("cardapio", "escola")
            .filter(
                escola=escola,
                cardapio__ativo=True,
                cardapio__data_inicio__lte=hoje,
                cardapio__data_fim__gte=hoje,
            )
            .first()
        )

        if not vinculo:
            context["sem_cardapio"] = True
            context["motivo"] = "Não há cardápio ativo para hoje."
            return context

        cardapio = vinculo.cardapio

        # ── 3. Semana atual ───────────────────────────────────────────
        numero_semana = self._calcular_semana(cardapio.data_inicio, hoje)

        semana = cardapio.semanas.filter(numero=numero_semana).first()

        if not semana:
            context.update({
                "sem_cardapio": True,
                "motivo": f"Semana {numero_semana} não cadastrada.",
                "cardapio": cardapio,
            })
            return context

        # ── 4. Dia da semana ──────────────────────────────────────────
        dia = semana.dias.filter(dia_semana=dia_semana_iso).first()

        if not dia:
            context.update({
                "sem_cardapio": True,
                "motivo": "Não há cardápio para hoje.",
                "cardapio": cardapio,
                "semana": semana,
            })
            return context

        # ── 5. Itens do dia ───────────────────────────────────────────
        itens = (
            CardapioItem.objects
            .filter(dia=dia)
            .select_related("tipo_refeicao", "receita")
            .prefetch_related(
                "receita__ingredientes__produto__unidade_medida"
            )
            .order_by("tipo_refeicao__nome", "ordem")
        )

        # Agrupamento por tipo de refeição
        refeicoes = {}
        for item in itens:
            tipo = item.tipo_refeicao.nome
            refeicoes.setdefault(tipo, []).append(item)

        # ── 6. Contexto final ─────────────────────────────────────────
        context.update({
            "cardapio": cardapio,
            "semana": semana,
            "dia": dia,
            "refeicoes": refeicoes,
            "sem_cardapio": not bool(refeicoes),
            "motivo": (
                "Nenhuma refeição cadastrada para hoje."
                if not refeicoes else None
            ),
        })

        return context