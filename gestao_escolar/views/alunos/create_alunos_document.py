from gestao_escolar.models import Alunos
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from datetime import datetime, date
from django.urls import reverse_lazy
from .partials_alunos.alunos_form import Aluno_documento_form


class Create_Alunos_Document(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Alunos
    form_class = Aluno_documento_form
    #form_class = Turma_form
    template_name = 'Escola/inicio.html'
    success_message = "Aluno registrado com sucesso!!"

    def get_success_url(self):
        aluno_id = self.kwargs['pk']
        return reverse_lazy('Gestao_Escolar:alunos_perfil', kwargs={'pk': aluno_id})  

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['aluno_create'] = Alunos.objects.filter(pk=self.kwargs['pk'])
        return kwargs

    def get_context_data(self, **kwargs):        
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Alunos'                  
        context['Alunos'] = Alunos.objects.all()
        context['now'] = datetime.now()
        context['conteudo_page'] = 'Registrar Alunos Documento'              
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."   
        return context
