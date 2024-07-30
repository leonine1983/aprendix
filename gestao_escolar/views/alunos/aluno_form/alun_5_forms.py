
from django import forms
from django.utils.safestring import mark_safe
from rh.models import Sexo
from gestao_escolar.models import (Alunos, Etnia, Nacionalidade,
                                     Pais_origem, Deficiencia_aluno)


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


class Alunos_form_etapa5(forms.ModelForm):            
    
    quilombola = forms.BooleanField(   
    label='Selecione se o aluno é Quilobola',
    widget = forms.CheckboxInput(attrs={'class': 'border border-info p-1 pb-1 bg-transparent text-info col m-2 rounded-1'}),
    required=False        
    )
    beneficiario_aux_Brasil = forms.BooleanField(   
    label='Selecione se o aluno é beneficiário do Bolsa Família/Aux. Brasil',
    widget = forms.CheckboxInput(attrs={'class': 'border border-info p-1 pb-1 bg-transparent text-info col m-2 rounded-1'}),
    required=False        
    )
    irmao_gemeo  = forms.BooleanField(   
    label='Selecione se o aluno tem irmão gêmeo',
    widget = forms.CheckboxInput(attrs={'class': 'border border-info p-1 pb-1 bg-transparent text-info col m-2 rounded-1'}),
    required=False        
    )
   
    class Meta:
        model = Alunos
        fields = ['quilombola', 'beneficiario_aux_Brasil', 'irmao_gemeo']
        