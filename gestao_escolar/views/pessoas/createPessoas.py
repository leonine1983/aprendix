from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from rh.models import Pessoas

class PessoasListView(LoginRequiredMixin, ListView):
    model = Pessoas
    template_name = 'pessoas_list.html'
    context_object_name = 'pessoas'
    login_url = '/login/'

class PessoasDetailView(LoginRequiredMixin, DetailView):
    model = Pessoas
    template_name = 'Escola/inicio.html'
    context_object_name = 'pessoa'
    

class PessoasCreateView(LoginRequiredMixin, CreateView):
    model = Pessoas
    template_name = 'Escola/inicio.html'
    fields = ['nome', 'sobrenome', 'sexo', 'data_nascimento',  'nome_profissao', 'cpf', 'rg', 'rua', 'complemento', 'numero_casa', 'bairro', 'cidade', 'cep']
    
    def form_valid(self, form):
        messages.success(self.request, 'Pessoa criada com sucesso!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao criar a pessoa. Verifique os dados e tente novamente.')
        return super().form_invalid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Pessoa criada com sucesso!')
        return reverse_lazy('Gestao_Escolar:pessoas-create')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['btn_bg'] = "btn-success"
        context['button'] = "Atualizar nome da escola"
        context['conteudo_page'] = 'Pessoa Create'
        context['pessoas'] = Pessoas.objects.all()
        # Preenche o formulário com a instância de Escola_admin
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."
        return context 

class PessoasUpdateView(LoginRequiredMixin, UpdateView):
    model = Pessoas
    template_name = 'pessoas_form.html'
    fields = ['nome', 'sobrenome', 'sexo', 'data_nascimento', 'idade', 'nome_profissao', 'cpf', 'rg', 'rua', 'complemento', 'numero_casa', 'bairro', 'cidade', 'cep']
    login_url = '/login/'

    def form_valid(self, form):
        messages.success(self.request, 'Pessoa atualizada com sucesso!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao atualizar a pessoa. Verifique os dados e tente novamente.')
        return super().form_invalid(form)

class PessoasDeleteView(LoginRequiredMixin, DeleteView):
    model = Pessoas
    template_name = 'pessoas_confirm_delete.html'
    success_url = reverse_lazy('pessoas-list')
    login_url = '/login/'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Pessoa excluída com sucesso!')
        return super().delete(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, 'Pessoa excluída com sucesso!')
        return response
