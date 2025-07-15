from django import forms
from rh.models import Escola, Escola_admin


class Escola_form(forms.ModelForm):
    class Meta:
        model = Escola
        fields =['nome_escola', 'sigla_escola']

        

class EscolaDados_form(forms.ModelForm):
    class Meta:
        model = Escola_admin
        exclude = ['nome']



