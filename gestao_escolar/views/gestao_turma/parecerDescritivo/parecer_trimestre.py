# views.py
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import generic
from gestao_escolar.models import GestaoTurmas, Matriculas, Trimestre, TurmaDisciplina, ParecerDescritivo
from .formsAlunoParecer import AlunoParecerForm

class GestaoTurmasParecer(generic.TemplateView):
    model = ParecerDescritivo
    fields = ['aspectos_cognitivos', 'aspectos_socioemocionais', 'aspectos_fisicos_motoras', 'habilidades', 'conteudos_abordados', 'interacao_social', 'comunicacao', 'consideracoes_finais', 'observacao_coordenador' ]
    template_name = 'Escola/inicio.html'

    def get_context_data(self, **kwargs):
        turma_id = self.kwargs['turma_id']
        context = super().get_context_data(**kwargs)
        parecer = get_object_or_404(ParecerDescritivo, matricula__turma = turma_id)
        form = AlunoParecerForm(instance = parecer)
        context['form'] = form

        context['turma'] = Matriculas.objects.filter(turma = turma_id)  
        context['trimestes'] = Trimestre.objects.all()
        context['conteudo_page'] = "Gestão Turmas - Parecer"
        return context
