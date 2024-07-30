from rh.models import Profissao
from django import forms


class Profissao_form(forms.ModelForm):
    nome_profissao = forms.CharField(
        label='Profissão:',
        widget=forms.TextInput(attrs={'class': 'form-control border p-3 pb-3 bg-transparent'}),
    )
    descricao = forms.CharField(
        label='Descreva a profissão:',
        widget=forms.Textarea(attrs={'class': 'form-control border p-3 pb-3 bg-transparent'}),
    )

    class Meta:
        model = Profissao
        fields = '__all__'

