from typing import Any
from django.forms import BaseModelForm
from django.http import HttpResponse
from django.views.generic import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from rh.models import Encaminhamentos, Escola, Contrato
from django.urls import reverse_lazy


class EncaminhaEscola (LoginRequiredMixin, CreateView, SuccessMessageMixin):
    model = Encaminhamentos
    fields = ['profissao']
    success_message = "Profissional Encaminhado para a sua escola com sucesso, para o ano letivo atual!!"
    template_name = 'Escola/inicio.html'

    def form_valid(self, form: BaseModelForm):
        escola_id = self.request.session['escola_id']
        ano_letivo = self.request.session['anoLetivo_id']
        print(f'anoletivo {ano_letivo}')
        pk = self.kwargs['pk']
        escola =  Escola.objects.get(id = escola_id)
        contrato = Contrato.objects.get(id = pk, ano_contrato = ano_letivo)
        form.instance.encaminhamento = contrato
        form.instance.destino = escola
        form.save()               
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('Gestao_Escolar:Professores_Pessoa_create')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Professores | Encaminhamento para a Escola'          
        context['lista_all'] = Encaminhamentos.objects.filter(encaminhamento = self.kwargs['pk'])
        context['conteudo_page'] = "encaminha_para_escola"   
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional. "        
        return context   