# forms.py
from django import forms
from gestao_escolar.models import GestaoTurmas, ParecerDescritivo

class AlunoParecerForm(forms.ModelForm):
    class Meta:
        model = ParecerDescritivo
        fields = ['aspectos_cognitivos', 'aspectos_socioemocionais', 'aspectos_fisicos_motoras', 'habilidades', 'conteudos_abordados', 'interacao_social', 'comunicacao', 'consideracoes_finais','resumo', 'observacao_coordenador' ]
        