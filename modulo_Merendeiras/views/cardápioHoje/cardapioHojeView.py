from django.views.generic import TemplateView
from django.utils import timezone
from core.groups.merenda import MerendeirasRequiredMixin
from core.views.baseMerendeira import BaseMerendeiraView

from merendaEscolar.models import (
    CardapioEscola,
    CardapioItem,
)



# views/cardapio_hoje.py  (método _calcular_semana substituído)

from django.views.generic import TemplateView
from django.utils import timezone

from core.groups.merenda import MerendeirasRequiredMixin
from core.views.baseMerendeira import BaseMerendeiraView
from utils  import numero_semana_no_mes   # ← novo utilitário

from merendaEscolar.models import (
    CardapioEscola,
    CardapioItem,
)



import calendar
from datetime import date

from django.views.generic import TemplateView
from django.utils import timezone

from core.views.baseMerendeira import BaseMerendeiraView
from merendaEscolar.models import CardapioEscola, CardapioItem


class CardapioHojeView(BaseMerendeiraView, TemplateView):
    """
    Exibe o cardápio do dia atual para a merendeira logada.
    A semana é calculada seguindo o calendário visual do mês (Dom–Sáb),
    reiniciando a contagem a cada mês.
    """

    template_name = "modulo_merendeiras/cadapioHoje/cardapio_hoje.html"

    # ------------------------------------------------------------------ #
    # Cálculo de semana — calendário visual (Dom → Sáb)                 #
    # ------------------------------------------------------------------ #

    def _semana_do_mes(self, data: date) -> int:
        """
        Retorna o número da semana do mês (1-based) seguindo o
        calendário visual com semanas de Domingo a Sábado.

        Exemplos:
          Maio/2026 começa na Sexta (col 5):
            dia 1  → (5+1-1)//7 + 1 = 5//7 + 1 = 0+1 = 1  ✓
            dia 2  → (5+2-1)//7 + 1 = 6//7 + 1 = 0+1 = 1  ✓  (sábado, ainda sem 1)
            dia 3  → (5+3-1)//7 + 1 = 7//7 + 1 = 1+1 = 2  ✓  (domingo, nova linha)
            dia 28 → (5+28-1)//7 + 1 = 32//7+1 = 4+1 = 5  ✓
        """
        primeiro = data.replace(day=1)
        # weekday() ISO: seg=0…dom=6 → convertemos para dom=0, seg=1…sáb=6
        col_primeiro = (primeiro.weekday() + 1) % 7
        return (col_primeiro + data.day - 1) // 7 + 1

    def _total_semanas_do_mes(self, ano: int, mes: int) -> int:
        """
        Retorna quantas linhas (semanas) o calendário visual do mês possui.
        Usa o mesmo critério Dom–Sáb.
        """
        ultimo_dia = date(ano, mes, calendar.monthrange(ano, mes)[1])
        return self._semana_do_mes(ultimo_dia)

    # ------------------------------------------------------------------ #
    # Recuperação do cardápio                                            #
    # ------------------------------------------------------------------ #

    def get_cardapio_do_dia(self, escola, hoje: date) -> dict:
        """
        Recupera o cardápio do dia para a escola especificada.
        A semana é identificada pelo calendário visual do mês corrente,
        garantindo que semanas inexistentes no mês sejam ignoradas.
        """
        dia_semana_iso = hoje.isoweekday()  # 1=Seg … 7=Dom

        if dia_semana_iso > 5:
            return {
                "sem_cardapio": True,
                "motivo": "Hoje é fim de semana. Não há merenda escolar.",
            }

        if not escola:
            return {
                "sem_cardapio": True,
                "motivo": "Seu usuário não está vinculado a nenhuma escola.",
            }

        # ── 1. Cardápio ativo que abranja a data de hoje ──────────────
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
                "motivo": "Não há cardápio ativo para hoje.",
            }

        cardapio = vinculo.cardapio

        # ── 2. Número da semana no calendário visual deste mês ────────
        numero_semana = self._semana_do_mes(hoje)

        # ── 3. Validação: semana existe neste mês? ────────────────────
        total_semanas = self._total_semanas_do_mes(hoje.year, hoje.month)
        if numero_semana > total_semanas:
            # Situação impossível pela própria construção da fórmula,
            # mas mantemos a guarda por segurança.
            return {
                "sem_cardapio": True,
                "motivo": (
                    f"Semana {numero_semana} não existe no calendário "
                    f"de {hoje.strftime('%B/%Y')} ({total_semanas} semanas)."
                ),
                "cardapio": cardapio,
            }

        # ── 4. Busca a semana no cardápio ──────────────────────────────
        semana = cardapio.semanas.filter(numero=numero_semana).first()

        if not semana:
            return {
                "sem_cardapio": True,
                "motivo": (
                    f"Semana {numero_semana} não cadastrada neste cardápio."
                ),
                "cardapio": cardapio,
                "numero_semana": numero_semana,
                "total_semanas": total_semanas,
            }

        # ── 5. Busca o dia da semana ───────────────────────────────────
        dia = semana.dias.filter(dia_semana=dia_semana_iso).first()

        if not dia:
            return {
                "sem_cardapio": True,
                "motivo": "Não há cardápio cadastrado para hoje.",
                "cardapio": cardapio,
                "semana": semana,
                "numero_semana": numero_semana,
                "total_semanas": total_semanas,
            }

        # ── 6. Itens do dia ────────────────────────────────────────────
        itens = (
            CardapioItem.objects
            .filter(dia=dia)
            .select_related("tipo_refeicao", "receita")
            .prefetch_related("receita__ingredientes__produto__unidade_medida")
            .order_by("tipo_refeicao__nome", "ordem")
        )

        refeicoes = {}
        for item in itens:
            tipo = item.tipo_refeicao.nome
            refeicoes.setdefault(tipo, []).append(item)

        return {
            "cardapio": cardapio,
            "semana": semana,
            "dia": dia,
            "refeicoes": refeicoes,
            "numero_semana": numero_semana,
            "total_semanas": total_semanas,
            "sem_cardapio": not bool(refeicoes),
            "motivo": (
                "Nenhuma refeição cadastrada para hoje." if not refeicoes else None
            ),
        }

    # ------------------------------------------------------------------ #
    # Contexto principal                                                 #
    # ------------------------------------------------------------------ #

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hoje = timezone.localdate()
        escola = self.get_escola_usuario()

        context["escola"] = escola
        context["hoje"] = hoje
        context["dia_semana_iso"] = hoje.isoweekday()

        context.update(self.get_cardapio_do_dia(escola, hoje))

        return context


"""
class CardapioHojeView(BaseMerendeiraView, TemplateView):
  

    template_name = "modulo_merendeiras/cadapioHoje/cardapio_hoje.html"

    # ------------------------------------------------------------------ #
    # Lógica principal do cardápio                                        #
    # ------------------------------------------------------------------ #

    def get_cardapio_do_dia(self, escola, hoje):

        # ── 1. Validações rápidas ─────────────────────────────────────
        if hoje.isoweekday() > 5:
            return {
                "sem_cardapio": True,
                "motivo": "Hoje é fim de semana. Não há merenda escolar.",
            }

        if not escola:
            return {
                "sem_cardapio": True,
                "motivo": "Seu usuário não está vinculado a nenhuma escola.",
            }

        # ── 2. Número da semana no calendário do mês atual ────────────
        numero_semana = numero_semana_no_mes(hoje)
        # numero_semana: int 1..5 (nunca None para datas válidas)

        # ── 3. Vínculo escola ↔ cardápio ativo que cobre hoje ─────────
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
                "motivo": "Não há cardápio ativo para hoje.",
            }

        cardapio = vinculo.cardapio

        # ── 4. Semana do cardápio pelo número do calendário ───────────
        #
        #   Se o cardápio tem 5 semanas mas o mês tem só 4, numero_semana
        #   jamais chegará a 5 — então a semana 5 do cardápio é ignorada
        #   automaticamente sem nenhum tratamento extra.
        #
        semana = cardapio.semanas.filter(numero=numero_semana).first()

        if not semana:
            return {
                "sem_cardapio": True,
                "motivo": (
                    f"Semana {numero_semana} não cadastrada neste cardápio."
                ),
                "cardapio": cardapio,
            }

        # ── 5. Dia da semana ──────────────────────────────────────────
        dia_semana_iso = hoje.isoweekday()   # 1=Seg … 5=Sex
        dia = semana.dias.filter(dia_semana=dia_semana_iso).first()

        if not dia:
            return {
                "sem_cardapio": True,
                "motivo": "Não há cardápio cadastrado para hoje.",
                "cardapio": cardapio,
                "semana": semana,
            }

        # ── 6. Itens do dia ───────────────────────────────────────────
        itens = (
            CardapioItem.objects
            .filter(dia=dia)
            .select_related("tipo_refeicao", "receita")
            .prefetch_related(
                "receita__ingredientes__produto__unidade_medida"
            )
            .order_by("tipo_refeicao__nome", "ordem")
        )

        refeicoes = {}
        for item in itens:
            tipo = item.tipo_refeicao.nome
            refeicoes.setdefault(tipo, []).append(item)

        # ── 7. Retorno ────────────────────────────────────────────────
        return {
            "cardapio": cardapio,
            "semana": semana,
            "dia": dia,
            "refeicoes": refeicoes,
            "numero_semana_calculado": numero_semana,   # útil para debug/template
            "sem_cardapio": not bool(refeicoes),
            "motivo": (
                "Nenhuma refeição cadastrada para hoje." if not refeicoes else None
            ),
        }

    # ------------------------------------------------------------------ #
    # Contexto da view                                                     #
    # ------------------------------------------------------------------ #

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hoje = timezone.localdate()
        escola = self.get_escola_usuario()

        context["escola"] = escola
        context["hoje"] = hoje
        context["dia_semana_iso"] = hoje.isoweekday()

        context.update(self.get_cardapio_do_dia(escola, hoje))
        return context
"""
"""
class CardapioHojeView(BaseMerendeiraView, TemplateView):
    

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
"""