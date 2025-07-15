from typing import Any
from django.forms import BaseModelForm
from django.views.generic import DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from rh.models import Encaminhamentos, Escola, Contrato,Ano
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect


class EncaminhaEscolaDelete(LoginRequiredMixin, DeleteView, SuccessMessageMixin):
    model = Encaminhamentos
    success_message = "Encaminhamento do profissional EXCLUÍDO com sucesso, para o ano letivo atual!!"
    template_name = 'Escola/inicio.html'

    def get_form_kwargs(self):
        return super().get_form_kwargs()
    
    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('Gestao_Escolar:Professores_Pessoa_create')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Professores | Encaminhamento para a Escola'     
        context['subtitulo_page'] = 'Atenção:<br> o encaminhamento do professor para o ano letivo será excluído, portanto, certifique-se de que essa é realmente sua decisão. Se houver algum lançamento feito pelo profissional no referido ano letivo, a exclusão não poderá ser realizada.'           
        context['buttom'] = 'Tem certeza que deseja apagar o encaminhamento de '
        context['lista_all'] = Encaminhamentos.objects.filter(encaminhamento__contratado = self.kwargs['pk'])
        context['conteudo_page'] = "encaminha_para_escola_deleteORupdate"   
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional. "        
        return context   