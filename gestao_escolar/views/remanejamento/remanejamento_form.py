from django import forms
from rh.models import Escola
from gestao_escolar.models import Turmas, Alunos, Remanejamento, Serie_Escolar, Matriculas

# widget personalizado que usa as classes (form-control, border, p-3, pb-3 e bg-transparent) para ser atribuido ao campo 'tempo_meses' 

remaneja_tipo = {        
    ('Desistente', 'Desistente/Evasão Escolar'),
    ('Transferido', 'Transferido'),
    ('mudou_turma', 'Mudança de turma')
}

class Matricula_form(forms.ModelForm):
    tipo = forms.ChoiceField(
        label="Tipo de remanejamento",
        choices=remaneja_tipo,
        widget = forms.Select(attrs={'class': 'border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1'}),  
          
    )      
    description = forms.CharField(
        label='Descreva o motivo do Remanejamento. Ex.: Escola para onde o aluno será remanejado e o porquê.',        
        widget=forms.Textarea(attrs={'class': 'border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1'}),
    )   
    
    class Meta:
        model = Remanejamento
        fields =['description', 'tipo']


class Turma_form(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)  # Obtém o request passado como argumento
        super().__init__(*args, **kwargs)
        
        # Use o request para filtrar o queryset
        if request:
            self.fields['turma'].queryset = Turmas.objects.filter(
                ano_letivo=request.session.get('anoLetivo_id'),
                escola=request.session.get('escola_nome')
            )

    class Meta:
        model = Matriculas
        fields =['turma']

