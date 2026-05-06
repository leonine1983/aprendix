from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages

from ...models import FichaExecucaoReceita, ExecucaoCardapioDia
from ..baseMerendeiraView import BaseMerendeiraView

from django import forms

from django.core.paginator import Paginator
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages
from django import forms

from ...models import FichaExecucaoReceita, ExecucaoCardapioDia
from ..baseMerendeiraView import BaseMerendeiraView


class FichaDiariaForm(forms.ModelForm):

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
            "aceitabilidade": forms.Select(attrs={
                "class": "form-select"
            }),
            "houve_sobras": forms.Select(attrs={
                "class": "form-select"
            }),
            "motivo_sobras": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Motivo das sobras (se houver)"
            }),
            "outra_ocorrencia": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Descreva outra ocorrência"
            }),
            "observacoes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),
        }
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages

from ...models import FichaExecucaoReceita, ExecucaoCardapioDia
from ..baseMerendeiraView import BaseMerendeiraView


class FichaDiariaCreateView(BaseMerendeiraView, CreateView):
    model = FichaExecucaoReceita
    form_class = FichaDiariaForm
    template_name = "modulo_merendeiras/cadapioHoje/ficha_diaria.html"

    def dispatch(self, request, *args, **kwargs):
        self.turno = self.kwargs.get("turno")

        self.execucao = ExecucaoCardapioDia.objects.get(
            pk=self.kwargs["execucao_id"],
            turno=self.turno
        )

        # 🔥 AGORA O FILTRO É POR execucao_cardapio_dia
        self.ficha_existente = FichaExecucaoReceita.objects.filter(
            execucao_cardapio_dia=self.execucao
        ).first()

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # 🔥 modo edição
        if self.ficha_existente:
            kwargs["instance"] = self.ficha_existente

        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["execucao"] = self.execucao
        ctx["modo_edicao"] = bool(self.ficha_existente)

        itens = []

        if self.ficha_existente:
            itens = self.ficha_existente.itens.select_related(
                "produto", "unidade"
            )
        else:
            itens_execucao = self.execucao.itens_executados.select_related(
                "execucao_receita"
            ).prefetch_related(
                "execucao_receita__movimentacoes__produto"
            )

            for item in itens_execucao:
                execucao_receita = item.execucao_receita

                if not execucao_receita:
                    continue

                for mov in execucao_receita.movimentacoes.all():
                    if mov.tipo != "RETIRADA_RECEITA":
                        continue

                    itens.append({
                        "produto_nome": mov.produto.nome,
                        "unidade": mov.produto.unidade_medida,
                        "quantidade": mov.quantidade,
                    })

        ctx["itens_alimentos"] = itens
        return ctx

    def form_valid(self, form):
        try:
            with transaction.atomic():

                ficha = form.save(commit=False)

                # 🔥 CAMPOS CORRETOS DO NOVO MODEL
                ficha.execucao_cardapio_dia = self.execucao
                ficha.usuario = self.request.user

                ficha.save()

                if self.ficha_existente:
                    messages.success(self.request, "Ficha atualizada com sucesso.")
                else:
                    messages.success(self.request, "Ficha registrada com sucesso.")

        except Exception as e:
            messages.error(self.request, f"Erro ao salvar ficha: {str(e)}")
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        return self.request.path