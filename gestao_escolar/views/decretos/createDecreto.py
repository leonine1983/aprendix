from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from rh.models import Pessoas, Decreto, Escola, Ano, DecretoAnoLetivoAtivo
from django.forms import ModelForm

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


class CriaDecreto_form(ModelForm):
    class Meta:
        model = Decreto
        fields = ['profissional', 'profissao', 'numero_decreto']
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if self.request:
            ano_atual = self.request.session.get('anoLetivo.id')
            profissionais_excluidos = Decreto.objects.exclude(ano_decreto__id=ano_atual).values_list('profissional_id', flat=True)
            self.fields['profissional'].queryset = Pessoas.objects.filter(id__in=profissionais_excluidos)
            print(f"profissional 2024 : {profissionais_excluidos}")




class DecretoCreateView(LoginRequiredMixin, CreateView):
    model = Decreto
    template_name = 'Escola/inicio.html'
    #form_class = CriaDecreto_form
    fields = ['profissional', 'profissao', 'numero_decreto']
    success_url = reverse_lazy('Gestao_Escolar:decreto-create')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # Obtem o ano letivo atual da sessão
        ano_atual_id = self.request.session.get('anoLetivo_id')

        # Lista de IDs de profissionais que já têm decreto no ano atual
        profissionais_com_decreto = Decreto.objects.filter(
            ano_decreto__id=ano_atual_id
        ).values_list('profissional_id', flat=True)

        # Altera o queryset do campo 'profissional' para excluir esses IDs
        form.fields['profissional'].queryset = Pessoas.objects.exclude(id__in=profissionais_com_decreto)

        return form

    def form_valid(self, form):
        name = form.instance.profissional
        cargo = form.instance.profissao
        messages.success(self.request, f'Decreto de {name} como {cargo} foi criado com sucesso!')
        form.instance.author_created = f'{self.request.user.first_name} {self.request.user.last_name}'
        form.instance.destino = Escola.objects.get(id=self.request.session['escola_id'])
        form.instance.ano_decreto = Ano.objects.get(id=self.request.session['anoLetivo_id'])
        form.instance.author_created = f'{self.request.user.first_name} {self.request.user.last_name}'        
        form.save()
        DecretoAnoLetivoAtivo.objects.create(
            decreto = Decreto.objects.get(id = form.instance.id),
            ano_ativo = Ano.objects.get(id = self.request.session['anoLetivo_id'])
        )        
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['titulo_page'] = 'Atualização de Dados Básicos da Escola'
        context['sub_titulo_page'] = "Use os campos abaixo para atualizar as informações básicas da Escola."
        context['btn_bg'] = "btn-success"
        context['button'] = "Criar decreto no Aprendix"
        context['conteudo_page'] = 'Decreto Create'
        context['decretos'] = Decreto.objects.filter(destino__id=self.request.session['escola_id'])
        context['decreto_ativo'] = DecretoAnoLetivoAtivo.objects.filter(ano_ativo = self.request.session['anoLetivo_id'], decreto__destino = self.request.session['escola_id'])
        # Preenche o formulário com a instância de Escola_admin
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."

        return context
    
# Decretto ativo ao ano
class DecretoAnoLetivoAtivo_create(LoginRequiredMixin,CreateView, SuccessMessageMixin):
    model = DecretoAnoLetivoAtivo
    fields = ['ano_ativo']
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('Gestao_Escolar:GE_inicio')
    success_message = "Decreto atualizado para o ano letivo atual"

    def form_valid(self, form, **kwargs):
        pk = self.kwargs['pk']
        profissional = Decreto.objects.get(id = pk)
        form.instance.decreto = profissional
        form.instance.author_created = f'{self.request.user.first_name} {self.request.user.last_name}'      
        return super().form_valid(form)   
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['conteudo_page'] = 'Decreto Ativo'
        context['decreto_ativo'] = DecretoAnoLetivoAtivo.objects.filter(ano_ativo = self.request.session['anoLetivo_id'], decreto__destino = self.request.session['escola_id'])
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."
        return context
    
