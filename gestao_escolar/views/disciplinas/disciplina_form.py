from django import forms
from gestao_escolar.models import Disciplina

# widget personalizado que usa as classes (form-control, border, p-3, pb-3 e bg-transparent) para ser atribuido ao campo 'tempo_meses' 

turno = {
    ('Matutino', 'Matutino'),
    ('Verspertino', 'Verspertino'),
    ('Noturno', 'Noturno')
}

class Diciplina_form(forms.ModelForm):
    
    nome = forms.CharField(
        #label='Nome da Turma:',
        widget=forms.TextInput(attrs={'class': ' border border-info p-1 pb-1 bg-transparent text-info m-2 rounded-1 w-75'}),
    ) 
    ordem_historico= forms.CharField(
        #label='Nome da Turma:',
        widget=forms.TextInput(attrs={'class': ' border border-info p-1 pb-1 bg-transparent text-info m-2 rounded-1 w-75'}),
    )     
   
    
    class Meta:
        model = Disciplina
        fields =['nome', 'ordem_historico']

