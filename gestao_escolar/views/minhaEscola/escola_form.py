from django import forms
from gestao_escolar.models import Turmas, Serie_Escolar
from rh.models import Escola


class Turma_form(forms.ModelForm):
    class Meta:
        model = Escola
        fields =['nome_escola','endereco_escola', 'telefone_escola']


