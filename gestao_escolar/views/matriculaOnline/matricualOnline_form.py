from django import forms
from django.utils.safestring import mark_safe
import random
import string
from rh.models import Uf_Unidade_Federativa, Sexo
from gestao_escolar.models import (Alunos, Cidade)
import re
from django.core.exceptions import ValidationError   
from django.contrib import messages                             

choices = {
    ('1','A+'),
    ('2','A-'),
    ('3','B+'),
    ('4','B-'),
    ('5','AB+'),
    ('6','AB-'),
    ('7','O+'),
    ('8','O-'),    
    ('0','Não informado')
}

# Validação de formulário
def validate_caracteres_especiais(value):
    if re.search(r"[~`´'^]", value):
        raise ValidationError('Não é permitido usar acentos ou caracteres especiais (~, `, ´, ^).')


class Alunos_form(forms.ModelForm):
    nome_completo = forms.CharField(
        label='Nome Completo (Igual ao do RG bem assim):',
        widget=forms.TextInput(attrs={
            'class': ' border border-info p-3 pb-3  text-uppercase col m-2 rounded-1',
            'autocomplete': 'off'}),        
    )
    
    def clean_nome_completo(self):
        nome_completo = self.cleaned_data.get('nome_completo')
        # Expressão regular para bloquear caracteres especiais e acentuados
        if re.search(r"[^a-zA-ZÇç\s]", nome_completo):
            mensagem_erro = "⚠️ Percebemos que você usou acento no 'Nome completo' do aluno. Evite acentos, números e caracteres especiais ❌ e tente novamente."        
            raise forms.ValidationError(mensagem_erro)
        return nome_completo   
    
    
    nome_mae = forms.CharField(      
        label=mark_safe('<i class="fa-solid fa-user-tie-hair"></i> Mãe'),
        widget=forms.TextInput(attrs={
            'class': ' border border-info p-3 pb-3  text-uppercase col m-2 rounded-1',
            'autocomplete': 'off'}),
    )

    def clean_nome_mae(self):
        nome_mae = self.cleaned_data.get('nome_mae')
        if re.search(r"[^a-zA-ZÇç\s]", nome_mae):
            mensagem_erro = "⚠️ Percebemos que você usou acento no 'Nome da mãe' do aluno. Evite acentos, números e caracteres especiais ❌ e tente novamente. Obrigado pela colaboração! 😄"    
            raise forms.ValidationError(mensagem_erro)
        return nome_mae    
    """
    class Meta:
        model = Alunos
        fields = ['nome_completo', 'nome_mae']"""    

    class Meta:
        validators=[validate_caracteres_especiais],  
        model = Alunos
        fields = ['nome_completo', 'nome_mae']


choice_estado_civil = {
    ('1', 'Solteiro'),
    ('2', 'Casado'),
    ('3', 'Separado'),
    ('4', 'Divorciado'),
    ('5', 'Viúvo'),
    ('6', 'União Estável'),
}
choice_modelo_certidao = {
    ('1', 'Antigo'),
    ('2', 'Novo'),
    ('3', 'Nenhuma')
}

choice_justifica_falta_document= {
    ('1', 'o(a) aluno(a) não possui os documentos pessoais solicitados'),
    ('2', 'A escola não dispõe ou não recebeu os docum. pessoais do(a) aluno(a)')    
}


class Aluno_documento_form(forms.ModelForm):   
    
    class Meta:
        model = Alunos
        fields = ['login_aluno', 'senha','email', 'rua', 'bairro', 'cidade' ]    
        
        """
        fields = ['login_aluno', 'senha','email',  'CPF', 'RG', 'RG_emissao', 'RG_UF', 'orgao_emissor','cidade_nascimento','estado','cidade',  'bairro', 'cartao_nacional_saude_cns', 'nis',
                'estado_civil', 'tipo_certidao', 'numero_certidao', 'livro', 'folha', 'termo', 'emissao', 'distrito_certidao', 'cartorio', 'comarca', 'cartorio_uf']    
        """
    
    
    login_aluno = forms.CharField(
        label='Login do aluno (idendificação de acesso do aluno ao Aprendix)',
        widget=forms.TextInput(attrs={'class': 'form-control  '}),
        required=False,
        disabled=True
    )   
    senha = forms.CharField(
        label='Senha do aluno (Senha Padrão 12345678)',
        widget=forms.PasswordInput(attrs={'class': 'form-control '}),
        required=False,
        disabled=True
    )
    email = forms.EmailField(
        label='Digite o email do aluno',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        #required=False
    )

    rua = forms.CharField(
        label="Rua, Av., Travessa",
        widget=forms.TextInput(attrs={'class': 'form-control '})        
    )

    estado = forms.ModelChoiceField(
        queryset = Uf_Unidade_Federativa.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False   
    )
    cidade_nascimento = forms.ModelChoiceField(
        queryset = Cidade.objects.all(),
        widget=forms.Select(attrs={'class': ' form-control'}),
        required=False   
    )
   
   
    CPF = forms.CharField(
        label='Número do CPF',
        widget=forms.TextInput(attrs={'class': 'form-control '}),
        required=False
    )
    RG = forms.CharField(
        label='Número do RG',
        widget=forms.TextInput(attrs={'class': 'form-control '}),
        required=False
    )
    RG_emissao = forms.DateField(
        label = "Data de emissão do RG",
        widget=forms.DateInput(attrs={'class': 'form-control ', 'type': 'date'}), 
        required=False 
    )
    RG_UF = forms.ModelChoiceField(
        label="UF do RG",
        queryset=Uf_Unidade_Federativa.objects.all(),
        widget=forms.Select(attrs={'class': ' form-control'}),  
        required=False   
    )
    orgao_emissor = forms.CharField(
        label="Órgão Emissor",
        widget=forms.TextInput(attrs={'class': 'form-control '}),
        required=False
    )
    
    
    
  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)        
        self.fields['login_aluno'].initial = self.generate_login()           
        self.fields['senha'].initial = "12345678"
                    
    
    def generate_login(self):
        while True:
            letra = random.choice(string.ascii_lowercase)
            numero = ''.join(random.choices(string.digits + string.digits, k=5))
            login = f'{letra}/{numero}'
            if not Alunos.objects.filter(login_aluno=login).exists():
                return login








"""

renda_familiar = forms.CharField(
        label='Renda Familiar',
        widget=forms.TextInput(attrs={'class': ' form-control'}),
        required=False
    )
  
    cartao_nacional_saude_cns = forms.CharField(
        label='Cartão Nacional de Saúde / CNS',
        widget=forms.TextInput(attrs={'class': 'form-control '}),
        required=False
    )
    nis = forms.CharField(
        label='NIS',
        widget=forms.TextInput(attrs={'class': ' form-control'}),
        required=False
    )
 
    estado_civil = forms.ChoiceField(
        label='Estado Civil',
        choices=choice_estado_civil,
        widget=forms.Select(attrs={'class': ' form-control'}),
        required=False
    )
    tipo_certidao = forms.ChoiceField(
        label='Tipo de Certidão',
        choices=choice_modelo_certidao,
        widget=forms.Select(attrs={'class': 'form-control '}),
        required=False
    )
    numero_certidao = forms.CharField(
        label='Número da Certidão',
        widget=forms.TextInput(attrs={'class': 'form-control '}),
        required=False
    )
    livro = forms.CharField(
        label='Livro',
        widget=forms.TextInput(attrs={'class': 'form-control '}),
        required=False
    )
    folha = forms.CharField(
        label='Folha',
        widget=forms.TextInput(attrs={'class': 'form-control '}),
        required=False
    )
    termo = forms.CharField(
        label='Termo',
        widget=forms.TextInput(attrs={'class': 'form-control '}),
        required=False
    )
    emissao = forms.DateField(
        label = "Data de emissão do RG",
        widget=forms.DateInput(attrs={'class': ' form-control'}), 
        required=False 
    )
    distrito_certidao = forms.CharField(
        label='Distrito',
        widget=forms.TextInput(attrs={'class': ' form-control', }),
        required=False
    )
    cartorio = forms.CharField(
        label='Cartório',
        widget=forms.TextInput(attrs={'class': 'form-control '}),
        required=False
    )
    comarca = forms.CharField(
        label='Comarca',
        widget=forms.TextInput(attrs={'class': 'form-control '}),
        required=False
    )
    cartorio_uf = forms.ModelChoiceField(
        label="UF do Cartório",
        queryset = Uf_Unidade_Federativa.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control border border-info p-2 pb-1   col m-2 rounded-1'}),
        required=False        
    )    
  
"""
