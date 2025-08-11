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
        fields = ['nome', 'descritivo_turma', 'turno', 'turma_multiserie', 'serie', 'quantidade_vagas']

    nome = forms.CharField(
        label='Nome da Turma (G1, G2, 1º, 2º ...):',
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center m-3 ',
            'placeholder': 'Ex.: 1º Ano, G1, G2...'
        })
    )
    descritivo_turma = forms.CharField(
        label='Descritivo da Turma (ex: única, A, B, C):',
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center m-3 ',
            'placeholder': 'Ex.: A, B, C, Única...'
        })
    )
    serie = forms.ModelChoiceField(
        queryset=Serie_Escolar.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select m-3'
        })
    )
    turno = forms.ChoiceField(
        choices=turno,
        widget=forms.Select(attrs={
            'class': 'form-select m-3'
        })
    )
    quantidade_vagas = forms.IntegerField(
        label='Quantidade de Vagas',
        widget=forms.NumberInput(attrs={
            'class': 'form-control text-center m-3',
            'placeholder': 'Ex.: 30'
        })
    )
    turma_multiserie = forms.BooleanField(
        required=False,
        label='Turma Multisseriada'
        
    )

