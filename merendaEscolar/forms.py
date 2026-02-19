from django import forms
from .models import EstoqueCentral, Produto


class EntradaEstoqueCentralForm(forms.Form):
    produto = forms.ModelChoiceField(
        queryset=Produto.objects.filter(ativo=True),
        label="Produto"
    )
    lote = forms.CharField(required=False, label="Lote")
    data_validade = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Data de Validade"
    )
    quantidade = forms.DecimalField(
        max_digits=14,
        decimal_places=2,
        min_value=0.01,
        label="Quantidade"
    )
    observacao = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Observação"
    )
