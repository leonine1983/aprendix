
from django import forms
from django.utils.safestring import mark_safe
from rh.models import Sexo
from gestao_escolar.models import (Alunos, Pais_origem)


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


class Alunos_form_etapa3(forms.ModelForm):

    aluno_exterior = forms.BooleanField(
        label="Marque somente se o aluno veio do exterior: "
    )    
    pais_origem = forms.ModelChoiceField(
        queryset=Pais_origem.objects.all(),
        widget=forms.Select(attrs={'class': ' border border-info p-1 pb-1 bg-transparent text-info col m-2 rounded-1'}),
        required=False,
        disabled = True
    )
    data_entrada_no_pais = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col2 m-2 rounded-1', 'type': 'date'}),      
        required=False,
        disabled = True
    )
    documento_estrangeiro = forms.CharField(        
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col m-2 rounded-1'}),
        required=False,
        disabled = True
    )
    class Meta:
        model = Alunos
        fields = ['aluno_exterior','pais_origem', 'data_entrada_no_pais', 'documento_estrangeiro']
        