from gestao_escolar.models import Turmas, TurmaDisciplina, Profissionais
from django.views.generic import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .disciplina_grade_form import Diciplina_Grade_form
from django.db.models import Q


class Create_Grades(LoginRequiredMixin, CreateView, SuccessMessageMixin):
    model = TurmaDisciplina
    #fields = "__all__"
    form_class = Diciplina_Grade_form
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')
    success_message = '✅ A disciplina e o professor foram adicionados à turma com sucesso.'

    
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

    def get_success_url(self):
        pk_value = self.kwargs['pk']
        return reverse_lazy('Gestao_Escolar:Grades_create', kwargs={'pk': pk_value})


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['turmas_query'] = Turmas.objects.filter(pk = self.kwargs['pk'])
        kwargs['professor_query'] = Profissionais.objects.filter(nome__encaminhamento__nome_escola = self.request.session['escola_id'], nome__encaminhamento__ano_contrato__anoletivo = self.request.session['anoLetivo_id'], cargo__nome = "Professor")
        

        return kwargs

    
    def get_context_data(self, **kwargs):        
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Grades'
        context['ativa'] = "Grades"
        
        context['conteudo_page'] = "Todas as turmas-grade"
        context['turma_ativa'] = Turmas.objects.get(pk = self.kwargs['pk'])
        context['turmas_disciplinas'] = self.get_queryset
        
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional.</div>"
        
        return context
            



            