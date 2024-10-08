# views.py
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import generic
from gestao_escolar.models import GestaoTurmas, Matriculas, Trimestre, TurmaDisciplina, ParecerDescritivo
from .formsParecer import GestaoParecerForm

class GestaoTurmasParecer(generic.CreateView):
    model = ParecerDescritivo
    fields = ['aspectos_cognitivos', 'aspectos_socioemocionais', 'aspectos_fisicos_motoras', 'habilidades', 'conteudos_abordados', 'interacao_social', 'comunicacao', 'consideracoes_finais', 'observacao_coordenador' ]
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('nome_da_sua_url_de_sucesso')  # Defina a URL de redirecionamento após o sucesso    

    """

    def get_initial(self):
        initial = super().get_initial()
        turma_id = self.kwargs['turma_id']
        initial['aluno'] = get_object_or_404(Matriculas, id=aluno_id) 
        return initial
    """
    def get_context_data(self, **kwargs):
        turma = self.kwargs['turma_id']
        context = super().get_context_data(**kwargs)
        context['turma'] = Matriculas.objects.filter(turma = turma)  
        context['trimestes'] = Trimestre.objects.all()
        context['conteudo_page'] = "Gestão Turmas - Parecer"
        return context
