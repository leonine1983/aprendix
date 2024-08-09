from gestao_escolar.models import TurmaDisciplina, Turmas, TurmaDisciplina, Profissionais
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy


class Delete_Grade(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = TurmaDisciplina
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')
    success_message = '✅ A disciplina e o professor foram excluídos da grade com sucesso'     

    def get_success_url(self):
        pk_value = self.object.turma.id        
        return reverse_lazy('Gestao_Escolar:Grades_create', kwargs={'pk': pk_value})    
    
    def get_context_data(self, **kwargs):        
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Grades'
        context['sub_titulo_page'] = 'Excluí disciplina na grade'
        context['ativa'] = "Grades"     
        context['bottom'] = "Exclui"      
        context['conteudo_page'] = "Updade_or_Delete Grade"
        context['turma_ativa'] = TurmaDisciplina.objects.get(pk = self.kwargs['pk']).turma
        context['turmas_disciplinas'] = self.get_queryset             
        return context            
