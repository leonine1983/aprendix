from gestao_escolar.models import Matriculas, Turmas
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from datetime import datetime, date
from django.urls import reverse_lazy
from .matriculas_form import MatriculaUpdate_form
from django.core.paginator import Paginator


class Update_Matricula(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Matriculas
    #form_class = Alunos_form
    form_class = MatriculaUpdate_form
    #fields = ['nome']
    template_name = 'Escola/inicio.html'
    success_message = "Atualizado com sucesso"
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')


    def get_context_data(self, **kwargs):     
        aluno = self.object
        aluno_turma = self.object.turma   
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Matrículas'          
        context['conteudo_page'] = "update"               
        context['page_ajuda'] = "<div class='border bg-secondary p-2'><h2>Pessoar a ser contratada</h2><div>"        
        context['titulo_page'] = f'Atualizar Matrícula de {aluno}'
        context['sub_Info_page'] = f"Use os campos abaixo para atualizar os dados de <b class='text-capitalize '>{aluno}</b> do {aluno_turma}"
        context['table'] = True   
        context['bottom'] = "Atualizar Informações"   
        context['btn_bg'] = " btn-secondary "  
        return context   