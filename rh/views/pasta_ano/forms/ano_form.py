from rh.models import Ano
from django import forms


class Ano_form(forms.ModelForm):
    ano = forms.CharField(
        label='ano:',
        widget=forms.TextInput(attrs={'class': 'form-control border p-3 pb-3 bg-transparent'}),
    )
    class Meta:
        model = Ano
        fields = '__all__'
