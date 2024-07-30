from rh.models import Pessoas
from django import forms


class Pessoas_form(forms.ModelForm):
    class Meta:
        model = Pessoas
        fields = ['nome', 'sobrenome', 'data_nascimento', 'nome_profissao',
                    'cpf', 'rg', 'rua', 'complemento', 'numero_casa', 'bairro',
                    'cep']
        
    nome = forms.CharField(
        label='Nome:',
        widget=forms.TextInput(attrs={'class': 'form-control border p-3 pb-3 bg-transparent'}),
    )
    sobrenome = forms.CharField(
        label='Sobrenome:',
        widget=forms.TextInput(attrs={'class': 'form-control border p-3 pb-3 bg-transparent '}),
    )

    

