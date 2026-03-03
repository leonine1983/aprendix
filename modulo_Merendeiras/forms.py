# modulo_Merendeiras/forms.py

from django import forms
from merendaEscolar.models import Receita, ReceitaIngrediente, Produto
from django.forms import inlineformset_factory
from ckeditor.widgets import CKEditorWidget

class ReceitaForm(forms.ModelForm):
    """
    Formulário institucional para criação/edição de receitas.
    - Nome obrigatório
    - Descrição e Modo de preparo com editor RichText
    - Ativa: status da receita
    """

    nome = forms.CharField(
        label="Nome da Receita",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ex.: Arroz com Legumes",
                "autofocus": True,
            }
        ),
    )

    descricao = forms.CharField(
        label="Descrição",
        required=False,
        widget=CKEditorWidget(config_name="default"),
        help_text="Informações gerais e observações da receita."
    )

    modo_preparo = forms.CharField(
        label="Modo de Preparo",
        widget=CKEditorWidget(config_name="default"),
        help_text="Passo a passo detalhado da receita."
    )

    ativa = forms.BooleanField(
        label="Ativa",
        required=False,
        initial=True,
        help_text="Receita disponível para execução pela escola."
    )

    class Meta:
        model = Receita
        fields = ["nome", "descricao", "modo_preparo", "ativa"]


# ============================
# FORMSET DE INGREDIENTES
# ============================

ReceitaIngredienteFormSet = inlineformset_factory(
    Receita,
    ReceitaIngrediente,
    fields=("produto", "quantidade"),
    extra=1,
    can_delete=True,
    widgets={
        "produto": forms.Select(attrs={"class": "form-select"}),
        "quantidade": forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
            }
        ),
    },
)