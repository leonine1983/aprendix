from rh.models import Escola
from gestao_escolar.models import Matriculas, Turmas
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime
from django.urls import reverse_lazy


class ViewDetailMatriculasTurma(LoginRequiredMixin, TemplateView):
    model = Matriculas
    #form_class = Turma_form
    template_name = 'Escola/inicio.html'
    
    def get_context_data(self, **kwargs):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48"><path d="M38-160v-94q0-35 18-63.5t50-4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM9-103.5T622-423q69 8 130 23.5t99 35.5q33 19 52 47t19 63v94H738ZM358-481q-66 0-108-4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM94B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM90 108 4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM96-23 21t-9 31v34Zm260-321q39 0 64.5-25.5T448-631q0-39-25.5-64.5T358-721q-39 0-64.5 25.5T268-631q0 39 25.5 64.5T358-541Zm0 321Zm0-411Z"/></svg>'
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Matrículas'          
        context['svg'] = svg 
        context['matriculas'] = Matriculas.objects.filter(turma=self.kwargs['pk'])        
        context['now'] = datetime.now()
        context['conteudo_page'] = "imprime_turma_matricula"               
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dado"
        # Quantidades
        context['matri_m'] = Matriculas.objects.filter(turma=self.kwargs['pk'], aluno__sexo__id = 1)
        
        return context
            



            