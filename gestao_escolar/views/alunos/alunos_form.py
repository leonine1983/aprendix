
from django import forms
from django.utils.safestring import mark_safe
import random
import string
from rh.models import Uf_Unidade_Federativa, Sexo
from gestao_escolar.models import (Alunos, Cidade)
                                     

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


class Alunos_form(forms.ModelForm):

    nome_completo = forms.CharField(
        label='Nome Completo (Igual ao do RG):',
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 text-info col m-2 rounded-1'}),
    )
    nome_mae = forms.CharField(      
        label=mark_safe('<i class="fa-solid fa-user-tie-hair"></i> Mãe'),
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 text-info col m-2 rounded-1'}),
    )
    class Meta:
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
        fields = ['aluno', 'CPF', 'RG', 'RG_emissao', 'RG_UF', 'orgao_emissor','cidade_nascimento','estado','renda_familiar','cidade',  'bairro', 'login_aluno', 'senha', 'cartao_nacional_saude_cns', 'nis', 'inep',
                'estado_civil', 'tipo_certidao', 'numero_certidao', 'livro', 'folha', 'termo', 'emissao', 'distrito_certidao', 'cartorio', 'comarca', 'cartorio_uf',
                'justificativa_falta_documento', 'local_diferenciado', 'obito', 'data_obito'  ]    
    
    aluno = forms.ModelChoiceField(
        queryset=Alunos.objects.none(),
        widget=forms.Select(attrs={'class': 'border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1',  'readonly': 'readonly'}),
        required=False
    )
    CPF = forms.CharField(
        label='Número do CPF',
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False
    )
    RG = forms.CharField(
        label='Número do RG',
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False
    )
    RG_emissao = forms.DateField(
        label = "Data de emissão do RG",
        widget=forms.DateInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col2 m-2 rounded-1', 'type': 'date'}), 
        required=False 
    )
    RG_UF = forms.ModelChoiceField(
        label="UF do RG",
        queryset=Uf_Unidade_Federativa.objects.all(),
        widget=forms.Select(attrs={'class': ' border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1'}),  
        required=False   
    )
    orgao_emissor = forms.CharField(
        label="Órgão Emissor",
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False
    )
    rua = forms.CharField(
        label="Rua, Av., Travessa",
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'})        
    )
    estado = forms.ModelChoiceField(
        queryset = Uf_Unidade_Federativa.objects.all(),
        widget=forms.Select(attrs={'class': ' border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1'}),
        required=False   
    )
    cidade_nascimento = forms.ModelChoiceField(
        queryset = Cidade.objects.all(),
        widget=forms.Select(attrs={'class': ' border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1'}),
        required=False   
    )
    renda_familiar = forms.CharField(
        label='Renda Familiar',
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False
    )
    login_aluno = forms.CharField(
        label='Login',
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False,
        disabled=True
    )   
    senha = forms.CharField(
        label='Senha do aluno',
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False,
        disabled=True
    )
    cartao_nacional_saude_cns = forms.CharField(
        label='Cartão Nacional de Saúde / CNS',
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False
    )
    nis = forms.CharField(
        label='NIS',
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False
    )
    inep = forms.CharField(
        label='INEP do Aluno',
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False
    )
    estado_civil = forms.ChoiceField(
        label='Estado Civil',
        choices=choice_estado_civil,
        widget=forms.Select(attrs={'class': ' border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False
    )
    tipo_certidao = forms.ChoiceField(
        label='Tipo de Certidão',
        choices=choice_modelo_certidao,
        widget=forms.Select(attrs={'class': ' border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False
    )
    numero_certidao = forms.CharField(
        label='Número da Certidão',
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False
    )
    livro = forms.CharField(
        label='Livro',
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False
    )
    folha = forms.CharField(
        label='Folha',
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False
    )
    termo = forms.CharField(
        label='Termo',
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False
    )
    emissao = forms.DateField(
        label = "Data de emissão do RG",
        widget=forms.DateInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col2 m-2 rounded-1', 'type': 'date'}), 
        required=False 
    )
    distrito_certidao = forms.CharField(
        label='Distrito',
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1', }),
        required=False
    )
    cartorio = forms.CharField(
        label='Cartório',
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False
    )
    comarca = forms.CharField(
        label='Comarca',
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False
    )
    cartorio_uf = forms.ModelChoiceField(
        label="UF do Cartório",
        queryset = Uf_Unidade_Federativa.objects.all(),
        widget=forms.Select(attrs={'class': ' border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1'}),
        required=False        
    )    
    justificativa_falta_documento = forms.ChoiceField(
        label='Justificativa da falta de documentação',
        choices=choice_justifica_falta_document,
        widget=forms.Select(attrs={'class': ' border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False
    )
    local_diferenciado = forms.CharField(
        label='Local Diferenciado',
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False
    )
    obito  = forms.BooleanField(   
        label='Óbito / Falecimento do aluno',
        widget = forms.CheckboxInput(attrs={'class': 'border border-info p-1 pb-1 bg-transparent text-info col m-2 rounded-1'}),
        required=False        
    )
    data_obito = forms.DateField(
        label = "Data óbito / Data de Falecimento",
        widget= forms.DateInput(attrs={'class': 'form-control border border-info p-3 pb-3  text-info col m-2 rounded-1', 'type': 'date'}),
        required=False  
    )

    def __init__(self, *args, **kwargs):
        aluno_create = kwargs.pop('aluno_create', None)
        super().__init__(*args, **kwargs)

        if aluno_create is not None:
            self.fields['aluno'].queryset = aluno_create
            self.fields['aluno'].initial = aluno_create.first()    
            self.fields['login_aluno'].initial = self.generate_login()           
            self.fields['senha'].initial = "12345678"
                    
    
    def generate_login(self):
        while True:
            letra = random.choice(string.ascii_lowercase)
            numero = ''.join(random.choices(string.digits + string.digits, k=5))
            login = f'{letra}/{numero}'
            if not Alunos.objects.filter(login_aluno=login).exists():
                return login

