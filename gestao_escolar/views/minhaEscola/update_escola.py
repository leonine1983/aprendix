from rh.models import Escola, Escola_admin, Prefeitura
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from datetime import datetime, date
from django.urls import reverse_lazy
from .escola_form import Escola_form, EscolaDados_form


class UpdateEscola(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Escola
    #form_class = Alunos_form
    form_class = Escola_form
    #fields = ['nome']
    template_name = 'Escola/inicio.html'
    success_message = "Turma atualizada com sucesso!!"
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')

    def form_valid(self, form):
        # Recupera a prefeitura da sessão e atribui ao objeto
        prefeitura_id = self.request.session.get('prefeitura')
        if prefeitura_id:
            form.instance.prefeitura = Prefeitura.objects.get(pk=prefeitura_id.id)   
            user_groups = self.request.user.groups.all()  
            if user_groups.exists():  
                last_group = user_groups.last()     
                form.instance.author_created = f'{self.request.user.first_name} {self.request.user.last_name} | {last_group.name}'
            else:
                form.instance.author_created = f'{self.request.user.first_name} {self.request.user.last_name} | No Group'      
        
        # Salva o objeto e armazena o ID
        response = super().form_valid(form)
        id = self.object.id
        
        # Cria um objeto Escola_admin com base no objeto recém-criado
        Escola_admin.objects.create(
            nome=Escola.objects.get(pk=id)
        )        
        return response


    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = self.get_object()

        # Verifica se existe uma instância de Escola_admin associada
        escola_admin_instance = getattr(escola, 'related_dadosEscola', None)
        if escola_admin_instance is None:
            # Cria uma instância vazia se não existir
            escola_admin_instance = Escola_admin()

        context['titulo_page'] = 'Atualização de Dados Básicos da Escola'
        context['sub_titulo_page'] = "Use os campos abaixo para atualizar as informações básicas da Escola."
        context['btn_bg'] = "btn-success"
        context['button'] = "Atualizar nome da escola"
        context['conteudo_page'] = 'Atualiza Escola'
        # Preenche o formulário com a instância de Escola_admin
        context['escola_dados_form'] = EscolaDados_form(instance=escola_admin_instance)
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."

        return context        
        