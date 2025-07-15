from django import forms
from django.forms import HiddenInput
from controle_estoque.models import Alimentos

class Forms_alimento(forms.ModelForm):
    class Meta: 
        model= Alimentos
        fields = ['categoria_alimento', 'nome']      

        widgets = {            
            'prefeitura': forms.Select(attrs={'disabled':True}),
            'prefeitura': HiddenInput(),
            'nome': forms.TextInput(attrs={'class':'form-control'}),
            'categoria_alimento': forms.Select(attrs={'class':'form-control'}),
            'quantidade_disponivel': forms.NumberInput(attrs={'class':'form-control'}),            
            'unidade': forms.TextInput(attrs={'class':'form-control'}),
            
            
        }



