from django.forms import BaseModelForm
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from rh.models import Cidade


class CidadeCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Cidade
    template_name = 'Escola/inicio.html'
    fields = "__all__"
    success_url = reverse_lazy('Gestao_Escolar:cidade-create')
    success_message = "Cidade criado com sucesso!!!"
     

    def get_context_data(self, **kwargs):
        busca = self.request.GET.get('busca-cidade')
        if busca:
            lista_all = Cidade.objects.filter(nome_cidade__icontains = busca)
        else:
            lista_all = Cidade.objects.all()

        lista_all = lista_all.order_by('nome_cidade')


        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Cidades'         
        #context['now'] = datetime.now()     
        context['conteudo_page'] = "Criar Cidade" 
        context['lista_all'] = lista_all
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."
        return context

class CidadeUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Cidade
    template_name = 'Escola/inicio.html'
    fields = "__all__"
    success_url = reverse_lazy('Gestao_Escolar:cidade-create')
    success_message = "Cidade atualizado com sucesso!!!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Cidades'         
        #context['now'] = datetime.now()     
        context['conteudo_page'] = 'update_or_delete'
        context['buttom'] = 'Atualizar o Cidade'   
        context['buttom_color'] = 'text-secondary btn-primary'      
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."
        return context

class CidadeDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Cidade
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('Gestao_Escolar:cidade-create')
    success_message = "Cidade excluído com sucesso"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Cidades'         
        context['buttom'] = 'Deseja excluir o cidade'   
        context['buttom_color'] = 'text-secondary btn-danger'        
        #context['now'] = datetime.now()     
        context['conteudo_page'] = 'update_or_delete'

        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."
        return context