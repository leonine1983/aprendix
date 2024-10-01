# forms.py
from django import forms
from gestao_escolar.models import GestaoTurmas

class GestaoParecerForm(forms.ModelForm):
    class Meta:
        model = GestaoTurmas
        fields = ['aluno', 'trimestre', 'parecer_descritivo']
        widgets = {
            'aluno': forms.HiddenInput(),
            'trimestre': forms.HiddenInput(),
        }
