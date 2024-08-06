from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from rh.models import Bairro

class BairroListView(ListView):
    model = Bairro
    template_name = 'Escola/inicio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Bairros'         
        #context['now'] = datetime.now()     
        context['conteudo_page'] = "Criar Bairros" 
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."
        return context

class BairroDetailView(DetailView):
    model = Bairro
    template_name = 'Escola/inicio.html'
    context_object_name = 'bairro'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Bairros'         
        #context['now'] = datetime.now()     
        context['conteudo_page'] = "Criar Bairros" 
        context['lista_all'] = Bairro.objects.all()
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."
        return context

class BairroCreateView(CreateView):
    model = Bairro
    template_name = 'Escola/inicio.html'
    fields = ['nome_cidade', 'nome_bairro']
    success_url = reverse_lazy('Gestao_Escolar:bairro-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Bairros'         
        #context['now'] = datetime.now()     
        context['conteudo_page'] = "Criar Bairros" 
        context['lista_all'] = Bairro.objects.all()
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."
        return context

class BairroUpdateView(UpdateView):
    model = Bairro
    template_name = 'Escola/inicio.html'
    fields = ['nome_cidade', 'nome_bairro']
    success_url = reverse_lazy('Gestao_Escolar:bairro-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Bairros'         
        #context['now'] = datetime.now()     
        context['conteudo_page'] = "Criar Bairros" 
        context['lista_all'] = Bairro.objects.all()
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."
        return context

class BairroDeleteView(DeleteView):
    model = Bairro
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('Gestao_Escolar:bairro-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Bairros'         
        #context['now'] = datetime.now()     
        context['conteudo_page'] = "Criar Bairros" 
        context['lista_all'] = Bairro.objects.all()
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."
        return context