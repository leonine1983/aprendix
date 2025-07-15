from django.views.generic import DetailView
from django.db.models import F
from collections import defaultdict
from gestao_escolar.models import Matriculas, GestaoTurmas, Serie_Escolar, Disciplina, Trimestre

class HistoricoEscolarAlunoView(DetailView):
    model = Matriculas
    template_name = 'Escola/inicio.html'
    context_object_name = 'matricula'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        matricula = self.object

        # Filtra registros de GestaoTurmas para a matrícula do aluno
        registros = GestaoTurmas.objects.filter(
            aluno=matricula,
            trimestre__final = True
        ).order_by('grade__disciplina__campo_conhecimento')

        disciplina_linguagens = Disciplina.objects.filter(campo_conhecimento ='linguagens')
        disciplina_matematica = Disciplina.objects.filter(campo_conhecimento ='matematica')
        disciplina_cienciasNatureza = Disciplina.objects.filter(campo_conhecimento ='ciencias_natureza')
        disciplina_cienciasHumanas = Disciplina.objects.filter(campo_conhecimento ='ciencias_humanas')
        disciplina_outras = Disciplina.objects.filter(campo_conhecimento ='outras')

        # Ordena por ano
        context['historico'] = registros
        context['serie'] =Serie_Escolar.objects.exclude(nivel_escolar__nome = 'Etapa Creche')
        context['disciplina'] =Disciplina.objects.all()
        context['trimestre'] = Trimestre.objects.exclude(final=True)
        context['conteudo_page'] = "historicoAluno"
        return context
