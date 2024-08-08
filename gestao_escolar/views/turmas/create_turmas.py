from rh.models import Escola
from gestao_escolar.models import Turmas, AnoLetivo
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime
from django.urls import reverse_lazy
from .turmas_form import Turma_form


class Create_turmas(LoginRequiredMixin, CreateView):
    model = Turmas
    # fields = ['nome']
    form_class = Turma_form
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_turmas')

    def form_valid(self, form):
        form.instance.escola = Escola.objects.get(id=self.request.session['escola_id'])
        form.instance.ano_letivo = AnoLetivo.objects.get(id=self.request.session['anoLetivo_id'])
        return super().form_valid(form)


    def get_context_data(self, **kwargs):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48"><path d="M38-160v-94q0-35 18-63.5t50-4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM9-103.5T622-423q69 8 130 23.5t99 35.5q33 19 52 47t19 63v94H738ZM358-481q-66 0-108-4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM94B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM90 108 4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM96-23 21t-9 31v34Zm260-321q39 0 64.5-25.5T448-631q0-39-25.5-64.5T358-721q-39 0-64.5 25.5T268-631q0 39 25.5 64.5T358-541Zm0 321Zm0-411Z"/></svg>'
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Turmas'          
        context['svg'] = svg 
        context['turmas'] = Turmas.objects.filter(escola = self.request.session['escola_id'], ano_letivo = self.request.session['anoLetivo_id'] )
        context['now'] = datetime.now()
        context['conteudo_page'] = 'Criar Turmas'       
        context['sub_title_context'] = 'Formulário de Registro de Turma para Gestão Escolar'            
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional. </b>"
        
        return context
            



            