# forms.py
from django import forms
from gestao_escolar.models import GestaoTurmas

class GestaoTurmasForm(forms.ModelForm):
    class Meta:
        model = GestaoTurmas
        fields = ['aluno', 'grade', 'trimestre', 'notas']
        widgets = {
            'aluno': forms.HiddenInput(),
            'trimestre': forms.HiddenInput(),
        }
