from django.views.generic import DetailView
from django.db.models import F
from collections import defaultdict
from gestao_escolar.models import Matriculas, GestaoTurmas, Serie_Escolar

class HistoricoEscolarAlunoView(DetailView):
    model = Matriculas
    template_name = 'Escola/impressos/historico_escolar.html'
    context_object_name = 'matricula'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        matricula = self.object

        # Filtra registros de GestaoTurmas para a matrícula do aluno
        registros = GestaoTurmas.objects.filter(
            aluno=matricula,
            trimestre__final = True
        )

        
        # Ordena por ano
        context['historico'] = registros
        context['serie'] =Serie_Escolar.objects.exclude(nivel_escolar__nome = 'Etapa Creche')
        return context
