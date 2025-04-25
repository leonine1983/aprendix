from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from rh.models import Pessoas, UserPessoas
from .professor_form import Pessoa_form, Pessoa_form_update
from django.contrib.auth.models import User, Group
from django.db import transaction, IntegrityError


class PessoasDetailView(LoginRequiredMixin, DetailView):
    model = Pessoas
    template_name = 'Escola/inicio.html'
    context_object_name = 'pessoa'



class PessoasCreateView(LoginRequiredMixin, CreateView):
    """
    View responsável por criar um novo registro de Pessoa no sistema, 
    juntamente com o usuário associado ao acesso do sistema.

    Esta view executa as seguintes operações dentro de uma transação atômica:
    1. Cria um novo usuário do sistema com os dados fornecidos no formulário.
    2. Adiciona o usuário ao grupo 'Professor'.
    3. Salva a instância de Pessoa no banco de dados.
    4. Cria um vínculo entre o usuário e a pessoa usando o modelo UserPessoas.

    Se ocorrer qualquer erro durante o processo, a transação é revertida 
    e uma mensagem de erro é exibida ao usuário.
    """
    model = Pessoas
    template_name = 'Escola/inicio.html'
    form_class = Pessoa_form

    def form_valid(self, form):
        try:
            with transaction.atomic():
                messages.success(self.request, 'Pessoa criada com sucesso!')

                nome = form.cleaned_data['nome']
                sobrenome = form.cleaned_data['sobrenome']
                email = form.cleaned_data['email']
                login = form.cleaned_data['login_professor']
                senha = form.cleaned_data['senha']

                # Cria o usuário
                user = User.objects.create_user(
                    first_name=nome,
                    last_name=sobrenome,
                    username=login,
                    password=senha,
                    email=email
                )

                # Adiciona ao grupo de professores
                professor_group = Group.objects.get(name='Professor')
                user.groups.add(professor_group)

                # Salva a pessoa
                self.object = form.save()

                # Cria o vínculo entre usuário e pessoa
                UserPessoas.objects.create(user=user, pessoa=self.object)

                messages.success(self.request, f'Acesso ao sistema liberado para {user.first_name} {user.last_name}')
                return super().form_valid(form)

        except IntegrityError as e:
            messages.error(self.request, f"Ocorreu um erro ao salvar os dados: {e}")
            return self.form_invalid(form)
        except Group.DoesNotExist:
            messages.error(self.request, "Grupo 'Professor' não encontrado.")
            return self.form_invalid(form)


    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao criar a pessoa. Verifique os dados e tente novamente.')
        return super().form_invalid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Pessoa criada com sucesso!')
        return reverse_lazy('Gestao_Escolar:pessoas-create')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['btn_bg'] = "btn-success"
        context['conteudo_page'] = 'Pessoa Create'
        context['pessoas'] = Pessoas.objects.all()
        context['rh_ativo'] = 'False'
        context['titulo_page'] = 'Cadastro de Pessoas'
        context['svg'] = '<i class="fa-duotone fa-address-card" style="--fa-secondary-color: #511f3c;"></i>'
        
        
        # Preenche o formulário com a instância de Escola_admin
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."
        return context 
    
    

class PessoasUpdateView(LoginRequiredMixin, UpdateView):
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
        context['conteudo_page'] = 'Update_Delete'        
        # Preenche o formulário com a instância de Escola_admin
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."
        return context 
    


class PessoasDeleteView(LoginRequiredMixin, DeleteView):
    model = Pessoas
    template_name = 'Escola/inicio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['btn_bg'] = "btn-danger"
        context['titulo_page'] = "Excluí pessoa do sistema"        
        context['button'] = "Excluir registro de "
        context['conteudo_page'] = 'Update_Delete'        
        return context 
    
    def get_success_url(self):
        messages.success(self.request, 'Pessoa Atualizada com sucesso!')
        return reverse_lazy('Gestao_Escolar:pessoas-create')
