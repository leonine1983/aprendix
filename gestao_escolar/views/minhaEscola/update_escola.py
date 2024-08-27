from rh.models import Escola
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from datetime import datetime, date
from django.urls import reverse_lazy
from .escola_form import Turma_form


class UpdateEscola(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Escola
    #form_class = Alunos_form
    form_class = Turma_form
    #fields = ['nome']
    template_name = 'Escola/inicio.html'
    success_message = "Turma atualizada com sucesso!!"
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Atualização de Dados Básicos da Escola'      
        context['sub_titulo_page']= "Use os campos abaixo para atualizar as informações básicas da Escola."    
        context['btn_bg'] = "btn-success"
        context['button'] = "Atualizar cadastro da"
        context['conteudo_page'] = 'Atualiza Escola'             
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."            
        
        return context