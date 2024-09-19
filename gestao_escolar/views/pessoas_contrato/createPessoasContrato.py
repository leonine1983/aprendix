from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from rh.models import Contrato, Pessoas,Profissao
from .contrato_form import Pessoa_form_update, Contrato_form
from django.db.models import Q

class PessoasContratoDetailView(LoginRequiredMixin, DetailView):
    model = Pessoas
    template_name = 'Escola/inicio.html'
    context_object_name = 'pessoa'
    

class PessoasContratoCreateView(LoginRequiredMixin, CreateView):
    model = Contrato
    template_name = 'Escola/inicio.html'
    form_class = Contrato_form
       
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['profissao_query'] = Profissao.objects.all(
            Q(nome_profissao='Diretor Escolar') |
            Q(nome_profissao='Vice-Diretor Escolar') |
            Q(nome_profissao='Coordenador Escolar') |
            Q(nome_profissao='Secretária escolar')
        )
        return kwargs
  
    
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
    
    """
    
    # widget personalizado que usa as classes (form-control, border, p-3, pb-3 e ) para ser atribuido ao campo 'tempo_meses' 

class Contrato(models.Model):
    #ano_contrato = models.ForeignKey(Ano, related_name='ano_contrato_related',verbose_name='Ano do contrato', on_delete=models.CASCADE)
    #contratado = models.ForeignKey(Pessoas, related_name='pessoa_contratada', verbose_name='Pessoa a ser contratada', on_delete=models.CASCADE)
    #text_contrato = models.ForeignKey(Texto_Contrato,related_name='Texto_contrao_related', null=True, blank=True, verbose_name='Vinculo com o tipo de contrato', on_delete=models.CASCADE)    
    
    #nome_escola = models.ForeignKey(Escola, null=True, verbose_name='Escola que o profissional irá desempenhar suas funções', on_delete=models.CASCADE)     
    

    #Segurança
    #created = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')    
    #author_created = models.CharField(max_length=50, null=True, blank=True, verbose_name='Autor da criação')
    #atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Data da Última Atualização')
    #author_atualiza = models.CharField(max_length=50, null=True, blank=True, verbose_name='Autor da atualização')

    #def calcula_data_fim_contrato(self):
        if self.tempo_meses and self.data_inicio_contrato:
            # Se os campos tempo_mese e data_inicio_contrato for adicionado pelo usuario
            self.data_fim_contrato = self.data_inicio_contrato + timedelta(days=self.tempo_meses * 30)

    def save(self, *args, **kwargs):
        self.calcula_data_fim_contrato()
        super().save(*args, **kwargs)

    class Meta :
        ordering = ['-ano_contrato']

    def __str__(self):
        return str(self.contratado)
    
    
    """

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
