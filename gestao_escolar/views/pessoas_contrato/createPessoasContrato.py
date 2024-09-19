from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from rh.models import Contrato, Pessoas,Profissao, Ano, Escola
from .contrato_form import Pessoa_form_update, Contrato_form
from django.db.models import Q

class PessoasContratoDetailView(LoginRequiredMixin, DetailView):
    model = Pessoas
    template_name = 'Escola/inicio.html'
    context_object_name = 'pessoa'
    

class PessoasContratoCreateView(LoginRequiredMixin, CreateView):
    model = Contrato
    template_name = 'Escola/inicio.html'
    fields = ['nome_profissao']
    

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Aplicar o filtro diretamente no queryset do campo 'nome_profissao'
        form.fields['nome_profissao'].queryset = Profissao.objects.exclude(
            Q(nome_profissao='Diretor Escolar') |
            Q(nome_profissao='Vice-Diretor Escolar') |
            Q(nome_profissao='Coordenador Escolar') |
            Q(nome_profissao='Secretária escolar')
        )
        return form
     
    
    def form_valid(self, form):
        ano_id = self.request.session['anoLetivo_id']
        escola_id  = self.request.session['escola_id']
        pessoa_id = self.kwargs['pk']        
        um =form.instance.contratado = Pessoas.objects.get(pk=pessoa_id)
        dois = form.instance.ano_contrato = Ano.objects.get(pk=ano_id)        
        tres =form.instance.nome_escola = Escola.objects.get(pk=escola_id)
        print(f'o que temos aqui um = {um}')
        print(f'o que temos aqui dois = {dois}')
        print(f'o que temos aqui tres = {tres}')
        form.save()
        messages.success(self.request, 'Contrato criado com sucesso!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao criar o Contrato. Verifique os dados e tente novamente.')
        return super().form_invalid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Contrato criado com sucesso!')
        return reverse_lazy('Gestao_Escolar:pessoas-create')
    
    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']       
        pessoa = Pessoas.objects.get(pk = pk)
        context = super().get_context_data(**kwargs)
        context['btn_bg'] = "btn-success"
        context['button'] = f"Criar Contrato de {pessoa}"
        context['conteudo_page'] = 'Contrato Create'
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
