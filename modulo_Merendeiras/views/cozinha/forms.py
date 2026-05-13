"""
modulo_merendeiras/forms.py
"""

from django import forms
from modulo_Merendeiras.models import ExecucaoCardapioDia


class ExecucaoCardapioForm(forms.Form):
    quantidade_alunos = forms.IntegerField(
        min_value=1,
        max_value=9999,
        label="Quantidade de alunos",
        widget=forms.NumberInput(attrs={
            'id': 'id_quantidade_alunos',
            'class': 'form-control form-control-lg',
            'placeholder': 'Ex: 150',
            'autocomplete': 'off',
        })
    )

    turno = forms.ChoiceField(
        choices=ExecucaoCardapioDia.TURNO_CHOICES,
        label="Turno",
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'})
    )