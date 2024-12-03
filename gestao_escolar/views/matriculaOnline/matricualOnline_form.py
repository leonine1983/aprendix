from django import forms
from django.utils.safestring import mark_safe
import random
import string
from rh.models import Uf_Unidade_Federativa, Sexo, Cidade, Bairro
from gestao_escolar.models import (Alunos, Pais_origem)
import re
from django.core.exceptions import ValidationError   
from django.contrib import messages     
from django import forms
from maskpass import askpass


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


class MatriculaOnline_etapa1(forms.ModelForm):   
    
    class Meta:
        model = Alunos
        fields = ['login_aluno', 'senha','nome_social','email']          
    
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
    nome_social = forms.CharField(
        label='Nome Social (Como a pessoa se identifica ou gosta de ser chamada)',
        widget=forms.TextInput(attrs={'class': 'form-control  '}),
        required=False,
    )  
    email = forms.EmailField(
        label='Digite o email do aluno (ex.: nome@gmail.com ou nome@hotmail.com)',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=True
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
                       

class MatriculaOnline_etapa2(forms.ModelForm):   
    class Meta:
        model = Alunos
        fields = ['nome_social', 'data_nascimento', 'sexo', 'tel_celular_aluno', 'etnia', 'rua', 'bairro', 'cidade', 'cartao_nacional_saude_cns', 'nis']      
        
    data_nascimento = forms.CharField(
        label="Data de nascimento do aluno",
        widget=forms.TextInput(attrs={'class': 'form-control ', 'type':'date'})        
    )
    tel_celular_aluno = forms.CharField(
        label="Telefone celular do aluno",
        widget=forms.TextInput(attrs={'class': 'form-control '})        
    )
    sexo = forms.ModelChoiceField(
        label="Gênero sexual do aluno",
        queryset = Sexo.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control '})        
    )   

    rua = forms.CharField(
        label="Rua, Av., Travessa",
        widget=forms.TextInput(attrs={'class': 'form-control '})        
    )
    bairro = forms.ModelChoiceField(
        label='Bairro',
        queryset = Bairro.objects.all(),
        widget=forms.Select(attrs={'class': ' form-control'}),
        required=False   
    )     
    cidade = forms.ModelChoiceField(
        label='Cidade onde o aluno mora',
        queryset = Cidade.objects.all(),
        widget=forms.Select(attrs={'class': ' form-control'}),
        required=False   
    )  
    estado = forms.ModelChoiceField(
        queryset = Uf_Unidade_Federativa.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False   
    )   

    cartao_nacional_saude_cns = forms.CharField(
        label='CNS (Cartão Nacional de Saúde)',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
    ) 

    nis = forms.CharField(
        label='NIS (Número de Identificação Social)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '16'}),
        required=False,
    )

class MatriculaOnline_etapa3(forms.ModelForm):   
    class Meta:
        model = Alunos
        fields = ['CPF', 'RG', 'RG_emissao', 'orgao_emissor', 'RG_UF', 'naturalidade', 'estado_naturalidade', 'nacionalidade', 'aluno_exterior', 'pais_origem', 'data_entrada_no_pais', 'documento_estrangeiro']      

    CPF = forms.CharField(
        label="CPF do aluno",
        widget=forms.TextInput(attrs={'class': 'form-control '})        
    )
    RG = forms.CharField(
        label="RG do aluno",
        widget=forms.TextInput(attrs={'class': 'form-control '})        
    )
    RG_emissao = forms.CharField(
        label="data de emissão do RG",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': "date"})            
    )   

    orgao_emissor = forms.CharField(
        label="Órgão que emitiu o RG",
        widget=forms.TextInput(attrs={'class': 'form-control'})        
    )
    RG_UF = forms.ModelChoiceField(
        label='Estado que emitiu o RG',
        queryset = Uf_Unidade_Federativa.objects.all(),
        widget=forms.Select(attrs={'class': ' form-control'}),
        required=False   
    )     
    naturalidade  = forms.ModelChoiceField(
        label='Cidade onde o aluno nasceu',
        queryset = Cidade.objects.all(),
        widget=forms.Select(attrs={'class': ' form-control'}),
        required=False,
    )  
    estado_naturalidade = forms.ModelChoiceField(
        queryset = Uf_Unidade_Federativa.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
    ) 
    pais_origem =  forms.ModelChoiceField(
        queryset=Pais_origem.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        disabled=True 
    )
    documento_estrangeiro =  forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        disabled=True 
    )
    data_entrada_no_pais = forms.DateField(  # Alterado de CharField para DateField
        label="Data de entrada no Brasil",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False,
        disabled=True 
    )

class MatriculaOnline_etapa4(forms.ModelForm):   
    class Meta:
        model = Alunos
        fields = ['estado_civil', 'tipo_certidao', 'numero_certidao', 'livro', 'folha', 'termo', 'emissao', 'distrito_certidao', 'cartorio', 'comarca', 'cartorio_uf']      
        
  



    


"""

     
             

  """

"""
  
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
