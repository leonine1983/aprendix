
from django import forms
from rh.models import Ano, Texto_Contrato, Pessoas, Contrato, Profissao, Escola, Salario

# widget personalizado que usa as classes (form-control, border, p-3, pb-3 e bg-transparent) para ser atribuido ao campo 'tempo_meses' 



class Contrato_form(forms.ModelForm):
    
    contratado = forms.ModelChoiceField(
        label='Pessoa a ser contratada:',
        queryset=Pessoas.objects.all(),  # Query to fetch all Pessoas objects
        widget=forms.Select(attrs={'class': 'form-control border p-3 pb-3 bg-transparent'}),
    )
    ano_contrato = forms.ModelChoiceField(
        label='Ano do contrato:',
        queryset=Ano.objects.all(),  # Query to fetch all Ano objects
        widget=forms.Select(attrs={'class': 'form-control border p-3 pb-3 bg-transparent'}),
    )
    
    text_contrato = forms.ModelChoiceField(
        label='Tipo de Contrato:',
        queryset=Texto_Contrato.objects.all(),  # Query to fetch all Ano objects
        widget=forms.Select(attrs={'class': 'form-control border p-3 pb-3 bg-transparent'}),
    )
    nome_profissao = forms.ModelChoiceField(
        label='Função que irá desempenhar na escola:',
        queryset=Profissao.objects.all(),  # Query to fetch all Ano objects
        widget=forms.Select(attrs={'class': 'form-control border p-3 pb-3 bg-transparent'}),
    )
    nome_escola = forms.ModelChoiceField(
        label='Escola que o profissional irá desempenhar suas funções:',
        queryset=Escola.objects.all(),  # Query to fetch all Ano objects
        widget=forms.Select(attrs={'class': 'form-control border p-3 pb-3 bg-transparent'}),
    )
    salario = forms.ModelChoiceField(
        label='Valor do salário para o cargo escolhido.Atente-se para o ano em que o valor do salário está vigente:',
        queryset=Salario.objects.all(),  # Query to fetch all Ano objects
        widget=forms.Select(attrs={'class': 'form-control border p-3 pb-3 bg-transparent'}),
    ) 
    tempo_meses = forms.IntegerField(
        label='Tempo em MESES que o profissional estará contratado pelo orgão',
       
    ) 
    
    
    class Meta:
        model = Contrato
        fields =['contratado', 'ano_contrato', 'text_contrato','nome_profissao', 'text_contrato', 'nome_profissao', 'nome_escola', 'salario', 'tempo_meses']

