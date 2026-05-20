"""
View: ExecucaoReceitaCozinhaFichaDiariaView
Gera/edita a Ficha Diária de Controle da Alimentação Escolar
a partir de uma instância de ExecucaoReceitaCozinha.

Coloque este arquivo em:
    modulo_merendeiras/views/execucao/ficha_diaria_execucao.py

(ou adicione ao arquivo de views existente)
"""

from django import forms
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView

from modulo_Merendeiras.models import (
    ExecucaoReceitaCozinha,
    ExecucaoCardapioDia,
    ExecucaoCardapioItem,
    FichaExecucaoReceita,
    MovimentacaoCozinha,
)
from core.views.baseMerendeira import BaseMerendeiraView

# ── Importações dos modelos de cardápio ──────────────────────────────────────
from merendaEscolar.models import CardapioDia, CardapioItem, CardapioSemana, CardapioEscola


# ============================================================
# Formulário (reaproveita os mesmos campos da FichaDiariaForm)
# ============================================================

class FichaDiariaExecucaoForm(forms.ModelForm):
    class Meta:
        model = FichaExecucaoReceita
        fields = [
            "porcoes_produzidas",
            "aceitabilidade",
            "houve_sobras",
            "motivo_sobras",
            "falta_alimento",
            "problema_equipamento",
            "falta_gas",
            "outra_ocorrencia",
            "observacoes",
        ]
        widgets = {
            "aceitabilidade": forms.Select(attrs={"class": "form-select"}),
            "houve_sobras":   forms.Select(attrs={"class": "form-select"}),
            "motivo_sobras": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Motivo das sobras (se houver)",
            }),
            "outra_ocorrencia": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Descreva outra ocorrência",
            }),
            "observacoes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


# ============================================================
# View principal
# ============================================================

class ExecucaoReceitaCozinhaFichaDiariaView(BaseMerendeiraView, CreateView):
    """
    Cria ou edita a Ficha Diária a partir de uma ExecucaoReceitaCozinha.

    URL sugerida:
        path(
            "execucao/<int:pk>/ficha-diaria/",
            ExecucaoReceitaCozinhaFichaDiariaView.as_view(),
            name="execucao_ficha_diaria",
        )
    """

    model        = FichaExecucaoReceita
    form_class   = FichaDiariaExecucaoForm
    template_name = "modulo_merendeiras/cozinha/ficha_diaria_execucaoCozinha.html"

    # ------------------------------------------------------------------
    # dispatch — carrega a ExecucaoReceitaCozinha e contextos derivados
    # ------------------------------------------------------------------
    def dispatch(self, request, *args, **kwargs):
        self.execucao_receita: ExecucaoReceitaCozinha = get_object_or_404(
            ExecucaoReceitaCozinha.objects.select_related("escola", "receita", "iniciado_por"),
            pk=self.kwargs["pk"],
        )

        # Tenta localizar ExecucaoCardapioDia compatível (mesma escola + data)
        self.execucao_dia: ExecucaoCardapioDia | None = (
            ExecucaoCardapioDia.objects
            .filter(
                escola=self.execucao_receita.escola,
                data=self.execucao_receita.iniciado_em.date(),
            )
            .first()
        )

        # Tenta localizar CardapioDia compatível com a data real da execução
        self.cardapio_dia: CardapioDia | None = self._resolver_cardapio_dia()

        # Verifica se já existe uma ficha para este ExecucaoCardapioDia
        self.ficha_existente: FichaExecucaoReceita | None = None
        if self.execucao_dia:
            self.ficha_existente = (
                FichaExecucaoReceita.objects
                .filter(execucao_cardapio_dia=self.execucao_dia)
                .first()
            )

        return super().dispatch(request, *args, **kwargs)

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    def _resolver_cardapio_dia(self) -> CardapioDia | None:
        """
        Localiza o CardapioDia cujo calendário corresponde à data da execução,
        respeitando o CardapioEscola vinculado à escola.
        """
        data = self.execucao_receita.iniciado_em.date()
        dia_semana = data.isoweekday()  # segunda=1 … sexta=5

        if dia_semana > 5:
            # Fim de semana — não há cardápio
            return None

        # Cardápios ativos vinculados à escola
        cardapios_ids = (
            CardapioEscola.objects
            .filter(escola=self.execucao_receita.escola)
            .values_list("cardapio_id", flat=True)
        )

        # Semanas cujo cardápio cobre a data
        semanas = (
            CardapioSemana.objects
            .filter(
                cardapio__id__in=cardapios_ids,
                cardapio__data_inicio__lte=data,
                cardapio__data_fim__gte=data,
                cardapio__ativo=True,
            )
            .select_related("cardapio")
        )

        for semana in semanas:
            try:
                return CardapioDia.objects.get(semana=semana, dia_semana=dia_semana)
            except CardapioDia.DoesNotExist:
                continue

        return None

    def _montar_controle_generos(self) -> list[dict]:
        """
        Retorna lista de dicts com os gêneros alimentícios consumidos
        na execução, calculados com base nas movimentações de estoque
        (MovimentacaoCozinha) ligadas à ExecucaoReceitaCozinha.
        """
        from collections import defaultdict

        agregado: dict[int, dict] = defaultdict(lambda: {
            "produto_nome": "",
            "unidade": "",
            "quantidade": 0.0,
        })

        movs = MovimentacaoCozinha.objects.filter(
            execucao_receita=self.execucao_receita,
            tipo="RETIRADA_RECEITA",
        ).select_related("produto", "produto__unidade_medida")

        for mov in movs:
            if not mov.produto:
                continue
            key = mov.produto.id
            agregado[key]["produto_nome"] = mov.produto.nome
            # unidade_medida pode ser FK com .simbolo ou CharField
            unidade = getattr(mov.produto, "unidade_medida", None)
            if unidade and hasattr(unidade, "simbolo"):
                agregado[key]["unidade"] = unidade.simbolo
            elif unidade:
                agregado[key]["unidade"] = str(unidade)
            agregado[key]["quantidade"] += float(mov.quantidade)

        # Fallback: se não houver movimentações, calcula por ingredientes × alunos
        if not agregado and self.execucao_receita.receita:
            alunos = self.execucao_receita.quantidade_alunos or 1
            for ing in self.execucao_receita.receita.ingredientes.select_related(
                "produto", "produto__unidade_medida"
            ).all():
                key = ing.produto.id
                unidade = getattr(ing.produto, "unidade_medida", None)
                simbolo = (
                    unidade.simbolo if unidade and hasattr(unidade, "simbolo")
                    else str(unidade) if unidade else ""
                )
                agregado[key]["produto_nome"] = ing.produto.nome
                agregado[key]["unidade"] = simbolo
                agregado[key]["quantidade"] += float(ing.quantidade) * alunos

        return list(agregado.values())

    # ------------------------------------------------------------------
    # Contexto
    # ------------------------------------------------------------------

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        exec_receita = self.execucao_receita

        # ── Identificação ───────────────────────────────────────────
        ctx["execucao_receita"] = exec_receita
        ctx["execucao_dia"]     = self.execucao_dia
        ctx["cardapio_dia"]     = self.cardapio_dia
        ctx["modo_edicao"]      = bool(self.ficha_existente)
        ctx["usuario_nome"]     = (
            self.request.user.get_full_name() or self.request.user.username
        )

        # ── Receitas previstas no cardápio do dia ────────────────────
        if self.cardapio_dia:
            ctx["receitas_previstas"] = (
                CardapioItem.objects
                .filter(dia=self.cardapio_dia)
                .select_related("receita", "tipo_refeicao")
            )
        else:
            ctx["receitas_previstas"] = []

        # ── Receita efetivamente executada ───────────────────────────
        ctx["receitas_executadas"] = [
            {
                "nome":   exec_receita.receita.nome,
                "status": exec_receita.get_status_display(),
                "porcoes": (
                    exec_receita.rendimento_real
                    or exec_receita.quantidade_alunos
                ),
                "motivo_falha": None,
            }
        ]

        # ── Gêneros alimentícios (controle de estoque) ───────────────
        ctx["itens_alimentos"] = self._montar_controle_generos()

        # ── Dados da execução para exibição no cabeçalho ─────────────
        ctx["escola"]           = exec_receita.escola
        ctx["data_execucao"]    = exec_receita.iniciado_em.date()
        ctx["turno_display"]    = (
            self.execucao_dia.get_turno_display()
            if self.execucao_dia else "—"
        )
        ctx["quantidade_alunos"] = (
            exec_receita.quantidade_alunos
            or (self.execucao_dia.quantidade_alunos if self.execucao_dia else None)
        )
        ctx["executado_por"] = exec_receita.iniciado_por

        return ctx

    # ------------------------------------------------------------------
    # Formulário
    # ------------------------------------------------------------------

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.ficha_existente:
            kwargs["instance"] = self.ficha_existente
        elif self.request.method == "GET":
            kwargs["initial"] = {
                "porcoes_produzidas": (
                    self.execucao_receita.quantidade_alunos
                    or self.execucao_receita.rendimento_real
                ),
            }
        return kwargs

    # ------------------------------------------------------------------
    # Salvar
    # ------------------------------------------------------------------

    def form_valid(self, form):
        # Garante que existe ExecucaoCardapioDia para vincular a ficha.
        # Se não existir, cria um registro mínimo para preservar a relação.
        if not self.execucao_dia:
            messages.error(
                self.request,
                "Não foi possível localizar uma Execução de Cardápio do Dia "
                "para vincular esta ficha. Certifique-se de que a execução "
                "foi criada corretamente.",
            )
            return self.form_invalid(form)

        try:
            with transaction.atomic():
                ficha = form.save(commit=False)
                ficha.execucao_cardapio_dia = self.execucao_dia
                ficha.usuario = self.request.user
                ficha.save()

                msg = "Ficha atualizada com sucesso." if self.ficha_existente else "Ficha registrada com sucesso."
                messages.success(self.request, msg)

        except Exception as exc:
            messages.error(self.request, f"Erro ao salvar ficha: {exc}")
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        return self.request.path