from gestao_escolar.models import Alunos, Turmas
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from datetime import datetime, date
from django.urls import reverse_lazy
from .alunos_form import *


class Delete_Alunos(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Alunos
    #form_class = Turma_form
    template_name = 'Escola/inicio.html'
    success_message = "excluído com sucesso"
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_alunos_create')


    def get_context_data(self, **kwargs):
        svg = '<i class="fa-sharp fa-solid fa-people fs-5"></i>'
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Excluir o cadastro do aluno'          
        context['svg'] = svg 
        context['btn_bg'] = " btn-danger "
        context['button'] = "Deletar cadastro de "
        context['Alunos'] = Alunos.objects.all()
        context['now'] = datetime.now()
        context['update'] = "update"
        
        context['conteudo_page'] = 'Registrar Alunos'            
        context['sub_Info_page'] = "EXCLUIR ALUNO"    
        context['sub_Info_page_h4'] =  "Excluir aluno do banco de dados"  
        context['oculta_tab'] = "true"
        context['table'] = True   
        context['bottom'] = "Deletar"        
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."            
        
        return context


   

