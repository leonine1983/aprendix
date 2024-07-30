from rh.models import Escola
from gestao_escolar.models import Matriculas, Turmas
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime
from django.urls import reverse_lazy


class ComprovanteMatricula(LoginRequiredMixin, DetailView):
    model = Matriculas
    #form_class = Turma_form
    template_name = 'Escola/inicio.html'
    
    def get_context_data(self, **kwargs):        
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Matrículas'          
        context['data_atual'] = datetime.today().date()
        context['matriculas'] = Matriculas.objects.filter(turma=self.kwargs['pk'])        
        context['now'] = datetime.now()
        context['conteudo_page'] = "imprime_comprovante_matricula"               
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dado"
        # Quantidades
        context['matri_m'] = Matriculas.objects.filter(turma=self.kwargs['pk'], aluno__sexo__id = 1)
        
        return context
            



            