from django import forms
from controle_estoque.models import Fornecedor


class FornecedorForm(forms.ModelForm):
    class Meta: 
        model =  Fornecedor
        fields = '__all__'    

    widgets = {
        'tipo' : forms.Select(attrs={'disabled' : True}),
        'local_destino' : forms.Select(attrs={'disabled' : True}),
    }
