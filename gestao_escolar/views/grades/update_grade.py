from gestao_escolar.models import TurmaDisciplina, Turmas, TurmaDisciplina, Profissionais
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from .disciplina_grade_form import Diciplina_Grade_form
from django.db.models import Q


class Update_Grade(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = TurmaDisciplina
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
        context['sub_titulo_page'] = 'Atualização da disciplina na grade'
        context['conteudo_page'] = "Updade_or_Delete Grade"  
        context['bottom'] = "Atualizar"     
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional.</div>"        
        return context            
