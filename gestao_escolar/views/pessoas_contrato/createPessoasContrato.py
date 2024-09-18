from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from rh.models import Pessoas
from .professorContrato_form import Pessoa_form, Pessoa_form_update


class PessoasContratoDetailView(LoginRequiredMixin, DetailView):
    model = Pessoas
    template_name = 'Escola/inicio.html'
    context_object_name = 'pessoa'
    

class PessoasContratoCreateView(LoginRequiredMixin, CreateView):
    model = Pessoas
    template_name = 'Escola/inicio.html'
    form_class = Pessoa_form
    
    def form_valid(self, form):
        messages.success(self.request, 'Contrato criado com sucesso!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao criar o Contrato. Verifique os dados e tente novamente.')
        return super().form_invalid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Contrato criado com sucesso!')
        return reverse_lazy('Gestao_Escolar:pessoas-create')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['btn_bg'] = "btn-success"
        context['button'] = "Criar Contrato"
        context['conteudo_page'] = 'Contrato Create'
        context['pessoas'] = Pessoas.objects.all()
        context['rh_ativo'] = 'False'
        
        # Preenche o formulário com a instância de Escola_admin
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."
        return context 

class PessoasContratoUpdateView(LoginRequiredMixin, UpdateView):
    model = Pessoas
    template_name = 'Escola/inicio.html'
    form_class = Pessoa_form_update

    def get_success_url(self):
        messages.success(self.request, 'Pessoa Atualizada com sucesso!')
        return reverse_lazy('Gestao_Escolar:pessoas-create')

    def form_valid(self, form):
        messages.success(self.request, 'Pessoa atualizada com sucesso!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao atualizar a pessoa. Verifique os dados e tente novamente.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['btn_bg'] = "btn-success"
        context['titulo_page'] = "Atualização de Informações Pessoais"        
        context['button'] = "Atualizar Informações de"
        context['conteudo_page'] = 'Contrato Update_Delete'     
        # Preenche o formulário com a instância de Escola_admin
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."
        return context 

class PessoasContratoDeleteView(LoginRequiredMixin, DeleteView):
    model = Pessoas
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('pessoas-list')
    login_url = '/login/'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Pessoa excluída com sucesso!')
        return super().delete(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, 'Pessoa excluída com sucesso!')
        return response
