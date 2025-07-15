from django.forms import BaseModelForm
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from rh.models import Bairro


class BairroCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Bairro
    template_name = 'Escola/inicio.html'
    fields = ['nome_cidade', 'nome_bairro']
    success_url = reverse_lazy('Gestao_Escolar:bairro-create')
    success_message = "Bairro criado com sucesso!!!"
     

    def get_context_data(self, **kwargs):
        busca = self.request.GET.get('busca-bairro')
        if busca:
            lista_all = Bairro.objects.filter(nome_bairro__icontains = busca)
        else:
            lista_all = Bairro.objects.all()

        lista_all = lista_all.order_by('nome_bairro')


        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Bairros'         
        #context['now'] = datetime.now()     
        context['conteudo_page'] = "Criar Bairros" 
        context['lista_all'] = lista_all
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."
        return context

class BairroUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Bairro
    template_name = 'Escola/inicio.html'
    fields = ['nome_cidade', 'nome_bairro']
    success_url = reverse_lazy('Gestao_Escolar:bairro-create')
    success_message = "Bairro atualizado com sucesso!!!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Bairros'         
        #context['now'] = datetime.now()     
        context['conteudo_page'] = 'update_or_delete'
        context['lista_all'] = Bairro.objects.all()
        context['buttom'] = 'Atualizar o bairro'   
        context['buttom_color'] = 'text-secondary btn-primary'      
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."
        return context

class BairroDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Bairro
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('Gestao_Escolar:bairro-create')
    success_message = "Bairro excluído com sucesso"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Bairros'         
        context['buttom'] = 'Deseja excluir o bairro'   
        context['buttom_color'] = 'text-secondary btn-danger'        
        #context['now'] = datetime.now()     
        context['conteudo_page'] = 'update_or_delete'
        context['lista_all'] = Bairro.objects.all()

        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."
        return context