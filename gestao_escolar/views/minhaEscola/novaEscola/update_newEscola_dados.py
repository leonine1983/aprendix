from rh.models import Escola, Escola_admin
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from datetime import datetime, date
from django.urls import reverse_lazy
from gestao_escolar.views.minhaEscola.escola_form import EscolaDados_form


class UpdateEscolaDados(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Escola_admin
    #form_class = Alunos_form
    form_class = EscolaDados_form
    #fields = ['nome']
    template_name = 'Escola/inicio.html'
    success_message = "Dados da escola atualizados com sucesso!!"
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Atualização de Dados Básicos da Escola'      
        context['sub_titulo_page']= "Use os campos abaixo para atualizar as informações básicas da Escola."    
        context['todas_escolas'] = Escola.objects.all()
        context['btn_bg'] = "btn-success"
        context['button'] = "Atualizar cadastro da"
        context['conteudo_page'] = 'CreateEscolaDados'             
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."  
        return context
    
   