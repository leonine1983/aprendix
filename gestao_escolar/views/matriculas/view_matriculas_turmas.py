from rh.models import Escola
from gestao_escolar.models import Matriculas, Turmas
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime
from django.urls import reverse_lazy
from django.http import Http404


class View_turmas_Matriculas(LoginRequiredMixin, ListView):
    model = Turmas
    #form_class = Turma_form
    template_name = 'Escola/inicio.html'

    def get_queryset(self):
        ano_letivo_id = self.request.session.get('anoLetivo_id')        
        
        if not ano_letivo_id:
            raise Http404("Ano Letivo não definido na sessão")
        
        # Filtrar as turmas pelo ano letivo da sessão
        queryset = Turmas.objects.filter(ano_letivo_id=ano_letivo_id, escola = Escola.objects.get(id = self.request.session['escola_id']))
        # Filtrar as matrículas pelas turmas obtidas
        print(f'ano livr {queryset}')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48"><path d="M38-160v-94q0-35 18-63.5t50-4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM9-103.5T622-423q69 8 130 23.5t99 35.5q33 19 52 47t19 63v94H738ZM358-481q-66 0-108-4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM94B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM90 108 4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM96-23 21t-9 31v34Zm260-321q39 0 64.5-25.5T448-631q0-39-25.5-64.5T358-721q-39 0-64.5 25.5T268-631q0 39 25.5 64.5T358-541Zm0 321Zm0-411Z"/></svg>'
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Matrículas'          
        context['svg'] = svg 
        context['now'] = datetime.now()
        context['conteudo_page'] = "Todas as matriculas"       
        
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional. "
        
        return context
            



            