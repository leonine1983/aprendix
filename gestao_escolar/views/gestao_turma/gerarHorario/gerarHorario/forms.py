from django import forms
from gestao_escolar.models import TurmaDisciplina

class HorarioForm(forms.Form):
    disciplinas = TurmaDisciplina.objects.all()
    for periodo in ['Manhã', 'Tarde', 'Noite']:
        for dia in ['segunda', 'terça', 'quarta', 'quinta', 'sexta']:
            locals()[f'{dia}_{periodo}'] = forms.ModelChoiceField(queryset=disciplinas, required=False)
