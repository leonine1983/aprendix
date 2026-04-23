from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages

from ...models import FichaDiaria, ExecucaoCardapioDia
from ..baseMerendeiraView import BaseMerendeiraView

from django import forms


class FichaDiariaForm(forms.ModelForm):

    class Meta:
        model = FichaDiaria
        fields = [
            "alunos_atendidos",
            "houve_alteracao_cardapio",
            "cardapio_executado",
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
            "alunos_atendidos": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Quantidade de alunos atendidos"
            }),
            "houve_alteracao_cardapio": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
            "cardapio_executado": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),
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


from django.core.paginator import Paginator

class FichaDiariaCreateView(BaseMerendeiraView, CreateView):
    model = FichaDiaria
    form_class = FichaDiariaForm
    template_name = "modulo_merendeiras/cadapioHoje/ficha_diaria.html"

    def dispatch(self, request, *args, **kwargs):
        self.turno = self.kwargs.get("turno")

        self.execucao = ExecucaoCardapioDia.objects.select_related(
            "escola",
            "cardapio_dia"
        ).get(
            pk=self.kwargs["execucao_id"],
            turno=self.turno  # 🔥 filtro por turno
        )

        self.ficha_existente = FichaDiaria.objects.filter(
            execucao=self.execucao
        ).first()

        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        """
        🔥 PRÉ-PREENCHIMENTO INTELIGENTE (reduz fricção cognitiva)
        """
        initial = super().get_initial()

        if not self.ficha_existente:
            initial.update({
                "cardapio_executado": str(self.execucao.cardapio_dia),
                "alunos_atendidos": str(self.execucao.quantidade_alunos),                
            })
            

        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # 🔥 MODO UPDATE automático
        if self.ficha_existente:
            kwargs["instance"] = self.ficha_existente

        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["execucao"] = self.execucao
        ctx["modo_edicao"] = bool(self.ficha_existente)
        return ctx

    def form_valid(self, form):
        try:
            with transaction.atomic():

                ficha = form.save(commit=False)

                ficha.execucao = self.execucao
                ficha.escola = self.execucao.escola
                ficha.data = self.execucao.data
                ficha.turno = self.execucao.turno
                ficha.tecnico_responsavel = self.request.user

                ficha.save()

                if self.ficha_existente:
                    messages.success(
                        self.request,
                        "Ficha atualizada com sucesso."
                    )
                else:
                    messages.success(
                        self.request,
                        "Ficha registrada com sucesso."
                    )

        except Exception as e:
            messages.error(self.request, f"Erro ao salvar ficha: {str(e)}")
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        return self.request.path