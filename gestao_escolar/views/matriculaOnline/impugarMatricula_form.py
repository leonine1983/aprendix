from gestao_escolar.models import MatriculasOnline, Matriculas
from .impugarMatricula_form import *
from django.forms import ModelForm  # Já importado diretamente

class MatriculasOnlineForm(ModelForm):  # Usando ModelForm diretamente
    class Meta:
        model = MatriculasOnline
        fields = ['id','impugnar', 'pendecia']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pendecia'].label = (
            'Por favor, descreva as pendências que precisam ser resolvidas para a finalização '
            'da matrícula ou que precisam ser entregues durante a primeira semana de aula. '
            'Isso pode incluir documentos pendentes, requisitos administrativos ou qualquer outro '
            'item que precise ser entregue ou regularizado.'
        )
        self.fields['impugnar'].label = ("Clique no botão 'Impugnar' para informar que a matrícula não pode"
                                         " ser confirmada e, em seguida, descreva o motivo no campo abaixo. ")
        
        self.fields['impugnar'].initial =  False
        self.fields['impugnar'].required = True







