from django import forms
from gestao_escolar.models import Turmas, Serie_Escolar

turno = {
    ('Matutino', 'Matutino'),
    ('Verspertino', 'Verspertino'),
    ('Noturno', 'Noturno')
}

class Turma_form(forms.ModelForm):
    class Meta:
        model = Turmas
        fields =['nome','descritivo_turma', 'turno', 'turma_multiserie', 'serie']
    
    nome = forms.CharField(
        label='Nome da Turma:',
        widget=forms.TextInput(attrs={'class': ' border border-info p-1 pb-1 text-center   m-2 rounded-1 col-2'}),
    )
    descritivo_turma = forms.CharField(
        label='Descritivo da Turma (ex: única, A, B, C):',
        widget=forms.TextInput(attrs={'class': ' border border-info p-1 pb-1 text-center  m-2 rounded-1 col-2'}),
    )
    serie = forms.ModelChoiceField(
        queryset= Serie_Escolar.objects.all(),
        widget=forms.Select(attrs={'class': ' border border-info p-1 pb-1 text-center   m-2 rounded-1 col-auto'}),
    ) 
    turno = forms.ChoiceField(
        choices= turno,
        widget= forms.Select(attrs={'class': ' border border-info p-1 pb-1 text-center  m-2 rounded-1 col-auto'})
    )  
    quantidade_vagas = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': ' border border-info p-1 pb-1 text-center   m-2 rounded-1 col-2'})
    )
