from gestao_escolar.models import Matriculas, Turmas, Remanejamento
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from .remanejamento_form import Matricula_form


class Create_Remanejamento(LoginRequiredMixin, CreateView):
    model = Remanejamento
    fields = '__all__'
    #form_class = Matricula_form
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')    
    success_message = "Aluno remanejado com sucesso!"
    
    def get_context_data(self, **kwargs):
        svg = '<i class="fa-sharp fa-regular fa-layer-plus"></i>'
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Remanejamento'          
        context['svg'] = svg 
        context['pk_aluno'] = self.kwargs['pk']
        context['info_matrilula'] = Matriculas.objects.filter(pk = self.kwargs['pk']) 
        context['conteudo_page'] = "Remaneja Aluno"  
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."        
        return context
            



            