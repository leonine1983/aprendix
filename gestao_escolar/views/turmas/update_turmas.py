from gestao_escolar.models import Alunos, Turmas
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from datetime import datetime, date
from django.urls import reverse_lazy
from .turmas_form import Turma_form


class UpdateTurmas(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Turmas
    #form_class = Alunos_form
    form_class = Turma_form
    #fields = ['nome']
    template_name = 'Escola/inicio.html'
    success_message = "Turma atualizada com sucesso!!"
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')


    def get_context_data(self, **kwargs):
        svg = '<i class="fa-sharp fa-solid fa-people fs-5"></i>'
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Atualização do Registro da Turma'      
        context['sub_titulo_page']= "Use os campos abaixo para atualizar as informações básicas da turma."    
        context['svg'] = svg 
        context['btn_bg'] = "btn-success"
        context['button'] = "Atualizar cadastro do"
        context['Alunos'] = Turmas.objects.all()
        context['now'] = datetime.now()
        context['conteudo_page'] = 'Criar Turmas update'             
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."            
        
        return context