
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
        label='Nome Completo do Aluno (Igual ao do RG bem assim):',
        widget=forms.TextInput(attrs={
            'class': 'form-control border border-info bg-light p-3 pb-3 text-info text-uppercase col m-2 rounded-1',
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
        label=mark_safe('<i class="fa-solid fa-user-tie-hair"></i>Nome completo da Mãe ou Responsável'),
        widget=forms.TextInput(attrs={
            'class': 'form-control border border-info p-3 pb-3 text-info text-uppercase col m-2 rounded-1',
            'autocomplete': 'off'}),
    )
    CPF_mae = forms.CharField(      
        label=mark_safe('<i class="fa-solid fa-user-tie-hair"></i>Digite o CPF da mãe ou responsável'),
        widget=forms.TextInput(attrs={
            'class': 'form-control border border-info p-3 pb-3 text-info text-uppercase col m-2 rounded-1',
            'autocomplete': 'off'}),    
    )

    def clean_nome_mae(self):
        nome_mae = self.cleaned_data.get('nome_mae')
        if re.search(r"[^a-zA-ZÇç\s]", nome_mae):
            mensagem_erro = "⚠️ Percebemos que você usou acento no 'Nome da mãe' do aluno. Evite acentos, números e caracteres especiais ❌ e tente novamente. Obrigado pela colaboração! 😄"    
            raise forms.ValidationError(mensagem_erro)
        return nome_mae    
    

    class Meta:
        validators=[validate_caracteres_especiais],  
        model = Alunos
        fields = ['nome_completo', 'nome_mae', 'CPF_mae']


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


import random
import string
from django import forms

class Aluno_documento_form(forms.ModelForm):   
    class Meta:
        model = Alunos
        fields = ['aluno', 'CPF', 'RG', 'RG_emissao', 'RG_UF', 'orgao_emissor','nacionalidade','estado_naturalidade', 
                 'cidade_naturalidade', 'estado', 'cidade', 'bairro', 'rua', 'login_aluno', 'senha', 
                 'cartao_nacional_saude_cns', 'nis', 'inep', 'estado_civil', 'tipo_certidao', 
                 'numero_certidao', 'livro', 'folha', 'termo', 'emissao', 'distrito_certidao', 
                 'cartorio', 'comarca', 'cartorio_uf', 'justificativa_falta_documento', 
                 'local_diferenciado', 'obito', 'data_obito']
    
    aluno = forms.ModelChoiceField(
        queryset=Alunos.objects.none(),
        widget=forms.Select(attrs={'class': 'border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1', 'readonly': 'readonly'}),
        required=False
    )
    
    # Alterado de ChoiceField para CharField para campos dinâmicos
    estado = forms.CharField(
        widget=forms.Select(attrs={
            'class': 'border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1',
            'id': 'id_estado',
            'onchange': 'carregarCidades()'
        }),
        required=False
    )
    
    cidade = forms.CharField(
        widget=forms.Select(attrs={
            'class': 'border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1',
            'id': 'id_cidade',
            'onchange': 'carregarBairros()',
            'disabled': 'disabled'
        }),
        required=False
    )
    
    bairro = forms.CharField(
        widget=forms.Select(attrs={
            'class': 'border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1',
            'id': 'id_bairro',
            'disabled': 'disabled'
        }),
        required=False
    )
    
    estado_naturalidade = forms.CharField(
        widget=forms.Select(attrs={
            'class': 'border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1',
            'id': 'id_estado_naturalidade',
            'onchange': 'carregarCidadesNaturalidade()'
        }),
        required=False
    )
    
    cidade_naturalidade = forms.CharField(
        widget=forms.Select(attrs={
            'class': 'border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1',
            'id': 'id_cidade_naturalidade',
            'disabled': 'disabled'
        }),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        # Remove o aluno_create dos kwargs antes de chamar o super()
        self.aluno_create = kwargs.pop('aluno_create', None)
        super().__init__(*args, **kwargs)
        
        if self.aluno_create is not None:
            self.fields['aluno'].queryset = self.aluno_create
            self.fields['aluno'].initial = self.aluno_create.first()    
            self.fields['login_aluno'].initial = self.generate_login()           
            self.fields['senha'].initial = "12345678"
        
        # Carrega os estados brasileiros
        estados_brasileiros = [
            ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
            ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
            ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
            ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
            ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
            ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
            ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')
        ]
        
        # Atualiza os widgets Select com as opções de estado
        self.fields['estado'].widget.choices = [('', 'Selecione um estado')] + estados_brasileiros
        self.fields['estado_naturalidade'].widget.choices = [('', 'Selecione um estado')] + estados_brasileiros
    
    def clean_cidade(self):
        """Validação personalizada para o campo cidade"""
        cidade = self.cleaned_data.get('cidade')
        # Aqui você pode adicionar validações adicionais se necessário
        return cidade
    
    def clean_cidade_naturalidade(self):
        """Validação personalizada para o campo cidade_naturalidade"""
        cidade = self.cleaned_data.get('cidade_naturalidade')
        # Aqui você pode adicionar validações adicionais se necessário
        return cidade
    
    def clean_bairro(self):
        """Validação personalizada para o campo bairro"""
        bairro = self.cleaned_data.get('bairro')
        # Aqui você pode adicionar validações adicionais se necessário
        return bairro
    
    def generate_login(self):
        while True:
            letra = random.choice(string.ascii_lowercase)
            numero = ''.join(random.choices(string.digits + string.digits, k=5))
            login = f'{letra}/{numero}'
            if not Alunos.objects.filter(login_aluno=login).exists():
                return login