
from django import forms
from django.utils.safestring import mark_safe
import random
import string
from rh.models import Uf_Unidade_Federativa, Sexo
from gestao_escolar.models import (Alunos)

                                     

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

"""
class Aluno_documento_form(forms.ModelForm):   
    class Meta:
        model = Alunos  # Certifique-se de usar o nome correto do modelo aqui
        fields = "__all__"

    # Definição dos campos do formulário
    aluno = forms.ModelChoiceField(
        queryset=Alunos.objects.none(),
        widget=forms.Select(attrs={'class': 'border border-info p-4 fs-3 pb-1 bg-transparent text-info col m-2 rounded-1', 'readonly': 'readonly'}),
        required=False
    )
    # Outros campos do formulário...
    login_aluno = forms.CharField(
        label='Login',
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False
    )   
    senha = forms.CharField(
        label='Senha do aluno',
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False
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
            """


class Aluno_documentoUpadate_form(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        aluno_create = kwargs.pop('aluno_create', None)
        super().__init__(*args, **kwargs)

        if aluno_create is not None:
            self.fields['aluno'].queryset = aluno_create
            self.fields['aluno'].initial = aluno_create.first()
            
    
    class Meta:
        model = Alunos
        fields = ['aluno', 'CPF', 'RG', 'RG_emissao', 'RG_UF', 'orgao_emissor','renda_familiar', 'cartao_nacional_saude_cns', 'nis', 'inep',
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
        widget= forms.DateInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1', 'type':'date'}),
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
    
    renda_familiar = forms.CharField(
        label='Renda Familiar',
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False
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

