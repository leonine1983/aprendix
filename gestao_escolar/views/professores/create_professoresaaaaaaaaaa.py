from gestao_escolar.models import Matriculas
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime
from django.urls import reverse_lazy
from .professor_form import Professor_form
from django.core.paginator import Paginator


class Create_Professores(LoginRequiredMixin, CreateView):
    model = Matriculas
    fields = '__all__'
    #form_class = Professor_form
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')        

    
    def get_context_data(self, **kwargs):
        svg = '<i class="fs-6 fa-duotone fa-person-chalkboard"></i>'
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Professores'          
        context['svg'] = svg 
        context['lista_all'] = Matriculas.objects.all()
        #context['now'] = datetime.now()     
        context['conteudo_page'] = "Professores"       
        
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."
        
        return context
            



            