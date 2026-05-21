from django.views.generic import TemplateView
from django.utils import timezone
from core.groups.merenda import MerendeirasRequiredMixin
from core.views.baseMerendeira import BaseMerendeiraView

from merendaEscolar.models import (
    CardapioEscola,
    CardapioItem,
)


class CardapioHojeView(BaseMerendeiraView, TemplateView):
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
    # NOVO MÉTODO EXTRAÍDO                                               #
    # ------------------------------------------------------------------ #
    def get_cardapio_do_dia(self, escola, hoje):
        """
        Recupera o cardápio do dia para a escola especificada.
        Retorna um dicionário com o contexto do cardápio.
        """
        dia_semana_iso = hoje.isoweekday()  # 1=Segunda … 7=Domingo

        # 🚫 Fim de semana
        if dia_semana_iso > 5:
            return {
                "sem_cardapio": True,
                "motivo": "Hoje é fim de semana. Não há merenda escolar."
            }

        # 🚫 Usuário sem escola
        if not escola:
            return {
                "sem_cardapio": True,
                "motivo": "Seu usuário não está vinculado a nenhuma escola."
            }

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
            return {
                "sem_cardapio": True,
                "motivo": "Não há cardápio ativo para hoje."
            }

        cardapio = vinculo.cardapio

        # ── 3. Semana atual ───────────────────────────────────────────
        numero_semana = self._calcular_semana(cardapio.data_inicio, hoje)
        semana = cardapio.semanas.filter(numero=numero_semana).first()

        if not semana:
            return {
                "sem_cardapio": True,
                "motivo": f"Semana {numero_semana} não cadastrada.",
                "cardapio": cardapio,
            }

        # ── 4. Dia da semana ──────────────────────────────────────────
        dia = semana.dias.filter(dia_semana=dia_semana_iso).first()

        if not dia:
            return {
                "sem_cardapio": True,
                "motivo": "Não há cardápio para hoje.",
                "cardapio": cardapio,
                "semana": semana,
            }

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

        # ── 6. Retorno do contexto ────────────────────────────────────
        return {
            "cardapio": cardapio,
            "semana": semana,
            "dia": dia,
            "refeicoes": refeicoes,
            "sem_cardapio": not bool(refeicoes),
            "motivo": (
                "Nenhuma refeição cadastrada para hoje."
                if not refeicoes else None
            ),
        }

    # ------------------------------------------------------------------ #
    # Contexto principal (atualizado)                                    #
    # ------------------------------------------------------------------ #
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hoje = timezone.localdate()
        escola = self.get_escola_usuario()

        # Dados base sempre disponíveis
        context["escola"] = escola
        context["hoje"] = hoje
        context["dia_semana_iso"] = hoje.isoweekday()

        # Adiciona dados do cardápio chamando o novo método
        context.update(self.get_cardapio_do_dia(escola, hoje))

        return context
