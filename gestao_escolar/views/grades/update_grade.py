from gestao_escolar.models import TurmaDisciplina, TurmaDisciplina
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy


class Update_Grade(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = TurmaDisciplina
    fields = ['disciplina', 'quant_aulas_semana', 'quant_aulas_dia', 'professor', 'professo2', 'reserva_tecnica', 'auxiliar_classe', 'carga_horaria_anual', 'limite_faltas']
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')
    success_message = '✅ A disciplina e o professor foram adicionados à turma com sucesso.'


    def get_success_url(self):
        pk_value = self.object.turma.id        
        return reverse_lazy('Gestao_Escolar:Grades_create', kwargs={'pk': pk_value})  
    
    def get_context_data(self, **kwargs):        
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Grades'
        context['sub_titulo_page'] = 'Atualização da disciplina na grade'
        context['conteudo_page'] = "Updade_or_Delete Grade"  
        context['bottom'] = "Atualizar"     
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional.</div>"        
        return context            
