# forms.py
from django import forms
from gestao_escolar.models import GestaoTurmas, ParecerDescritivo

# forms.py
class AlunoParecerForm(forms.ModelForm):
    class Meta:
        model = ParecerDescritivo
        fields = ['trimestre', 'aspectos_cognitivos', 'aspectos_socioemocionais', 'aspectos_fisicos_motoras', 'habilidades', 'conteudos_abordados', 'interacao_social', 'comunicacao', 'consideracoes_finais', 'resumo', 'observacao_coordenador']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.trimestre:
            # Ajuste conforme o seu modelo
            self.fields['trimestre'].label = self.instance.trimestre.id # Supondo que 'nome' seja o atributo correto
