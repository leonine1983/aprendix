from gestao_escolar.models import Turmas
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from datetime import datetime, date
from django.urls import reverse_lazy
from .escola_form import Turma_form


class Delete_Turmas(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Turmas
    template_name = 'Escola/inicio.html'
    success_message = "Deletado com sucesso"
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')


    def get_context_data(self, **kwargs):
        svg = '<i class="fa-sharp fa-solid fa-people fs-5"></i>'
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Exclusão da Turma' 
        context['sub_titulo_page']= "Você está prestes a excluir esta turma. Tem certeza de que deseja continuar? Após a exclusão, não será possível recuperar a turma."  
        context['svg'] = svg 
        context['btn_bg'] = " btn-danger "
        context['button'] = "Deletar cadastro do"
        context['Alunos'] = Turmas.objects.all()
        context['now'] = datetime.now()
        context['update'] = "update"        
        context['conteudo_page'] = 'Criar Turmas update'           
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."      
        return context
