from rh.models import Contrato
from django import forms
from ckeditor.fields import RichTextField
from rh.models import Ano, Texto_Contrato, Pessoas



class Texto_contrato_form(forms.ModelForm):

    TIPO_CHOICES = [
        ('professor', 'Professor'),
        ('funcionario', 'Funcionário'),
        ('estagio', 'Estágio'),
        ('voluntario', 'Voluntário')
    ]

    tipo = forms.ChoiceField(
        label='Tipo de Contrato:',
        choices=TIPO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control border p-3 pb-3 bg-transparent'}),
    )

    texto = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 100, 'class': 'form-control'}),  # Defina o número de linhas desejado
    )

    class Meta:
        model = Texto_Contrato
        fields = ['tipo', 'texto']

