from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from rh.models import Decreto

class DecretoListView(LoginRequiredMixin, ListView):
    model = Decreto
    template_name = 'decreto_list.html'
    context_object_name = 'decretos'
    login_url = '/login/'  # URL para redirecionar se o usuário não estiver autenticado

class DecretoDetailView(LoginRequiredMixin, DetailView):
    model = Decreto
    template_name = 'decreto_detail.html'
    context_object_name = 'decreto'
    login_url = '/login/'  # URL para redirecionar se o usuário não estiver autenticado

class DecretoCreateView(LoginRequiredMixin, CreateView):
    model = Decreto
    template_name = 'Escola/inicio.html'
    fields = ['profissional', 'destino', 'profissao', 'ano_decreto']
    success_url = reverse_lazy('Gestao_Escolar:decreto-create')

    def form_valid(self, form):
        messages.success(self.request, 'Decreto criado com sucesso!')
        form.instance.author_created = f'{self.request.user.first_name} {self.request.user.last_name}'
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['titulo_page'] = 'Atualização de Dados Básicos da Escola'
        context['sub_titulo_page'] = "Use os campos abaixo para atualizar as informações básicas da Escola."
        context['btn_bg'] = "btn-success"
        context['button'] = "Atualizar nome da escola"
        context['conteudo_page'] = 'Decreto Create'
        context['decretos'] = Decreto.objects.filter(destino__id=self.request.session['escola_id'])
        # Preenche o formulário com a instância de Escola_admin
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."

        return context        
