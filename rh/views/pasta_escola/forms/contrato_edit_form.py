from rh.models import Contrato
from django import forms


class Contrato_edit_form(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = ['text_contrato']

