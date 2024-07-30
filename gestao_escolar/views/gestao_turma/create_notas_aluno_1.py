from gestao_escolar.models import Turmas, GestaoTurmas, Trimestre, Profissionais, Matriculas
from rh.models import Encaminhamentos
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .disciplina_notasAlunos_form import NotasAlunos_All_form
from django.db.models import Q


class Create_Notas(LoginRequiredMixin, CreateView):
    model = GestaoTurmas
    #fields = "__all__"
    form_class = NotasAlunos_All_form
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')

    """
    def get_queryset(self):
        buscar_turma = self.request.GET.get ('busca-turma')
        if buscar_turma:
            turmas = TurmaDisciplina.objects.filter(
                                Q(discipina__nome__icontains = buscar_turma)
                                and Q(turma__ano_letivo = self.request.session("anoLetivo_id")) 
                                and Q(turma = self.kwargs['pk']))
        else:
            turmas = TurmaDisciplina.objects.filter(turma = self.kwargs['pk'])

        return turmas






    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['turmas_query'] = Turmas.objects.filter(pk = self.kwargs['pk'])
        kwargs['professor_query'] = Profissionais.objects.filter(nome__encaminhamento__nome_escola = self.request.session['escola_id'], nome__encaminhamento__ano_contrato__anoletivo = self.request.session['anoLetivo_id'], cargo__nome = "Professor")
        return kwargs"""

    
    def get_context_data(self, **kwargs):        
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Gestão de Turmas'
        
        context['turmas'] = Turmas.objects.filter(escola = self.request.session['escola_id'], ano_letivo = self.request.session['anoLetivo_id'])
        context['ativa'] = "Grades"
        #context['alunos'] = Matriculas.objects.all()
        context['conteudo_page'] = "Gestão Turmas"
        context['turmas_disciplinas'] = self.get_queryset        
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."      
        return context
            



            