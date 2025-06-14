
from django import forms
from django.utils.safestring import mark_safe
from rh.models import Sexo
from gestao_escolar.models import (Alunos, Etnia, Nacionalidade,
                                     Pais_origem, Deficiencia_aluno, Cidade)


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

LATERALIDADE_CHOICES = [
    ('destro', 'Destro'),
    ('canhoto', 'Canhoto'),
    ('ambidestro', 'Ambidestro'),
]

class Alunos_form_etapa2(forms.ModelForm):

    nome_social = forms.CharField(
        label='Nome Social (Se possuir):',
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False
    )   
    data_nascimento = forms.DateField(
        label='Data de Nascimento:',
        widget=forms.DateInput(attrs={'class': 'form-control border border-info p-3 pb-3  text-info col2 m-2 rounded-1', 'type':'date' }),        
    )
    
    sexo = forms.ModelChoiceField(
        label='Sexo:',
        queryset=Sexo.objects.all(),
        widget=forms.Select(attrs={'class': ' border border-info p-1 pb-1 bg-transparent text-info col m-2 rounded-1'}),
    )
    
    etnia = forms.ModelChoiceField(
        queryset=Etnia.objects.all(),
        widget=forms.Select(attrs={'class': ' border border-info p-1 pb-1 bg-transparent text-info col m-2 rounded-1'}),
    )
    tel_celular_aluno = forms.CharField(   
        label=mark_safe('<i class="fa-brands fa-whatsapp text-success"></i> Telefone celular do aluno'),   
        widget=forms.TextInput(attrs={
            'class': 'form-control  border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1',
            'type': 'tel'}),
        required=True
    )
    
    email = forms.CharField(        
        widget=forms.EmailInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1', 'type': 'email'}),
        required=False
    )
   
    tel_celular_mae = forms.CharField(  
        label=mark_safe('<i class="fa-brands fa-whatsapp text-success"></i> Telefone celular da mãe'),      
        widget=forms.TextInput(attrs={'class': 'form-control  border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1', 'type': 'tel'}),
        required=False
    )
    nome_pai = forms.CharField(        
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False
    )
    
    tel_celular_pai = forms.CharField(      
        label=mark_safe('<i class="fa-brands fa-whatsapp text-success"></i> Telefone celular do pai'),    
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1', 'type': 'tel'}),
        required=False
    )
    foto_aluno = forms.ImageField(
        required=False
    )
    
    lateralidade = forms.ChoiceField(
        label='Lateralidade (mão dominante):',
        choices=LATERALIDADE_CHOICES,
        required=False,
        help_text='Destro: usa a mão direita • Canhoto: usa a mão esquerda • Ambidestro: usa ambas as mãos',
        widget=forms.Select(attrs={
            'class': 'form-control border border-info p-2 bg-transparent text-info col m-2 rounded-1'
        }),
    )

    class Meta:
        model = Alunos
        fields = [
            'nome_social', 'data_nascimento', 'sexo', 'etnia',
            'tel_celular_aluno', 'email', 'tel_celular_mae',
            'nome_pai', 'tel_celular_pai',  'foto_aluno', 'lateralidade'
        ]