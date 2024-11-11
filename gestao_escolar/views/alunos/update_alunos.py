from gestao_escolar.models import Alunos, Turmas
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from datetime import datetime, date
from django.urls import reverse_lazy
from .partials_alunos.alunos_form import *
from gestao_escolar.views.alunos.aluno_form.alun_completo_update import Alunos_atualiza


class Update_Alunos(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Alunos
    form_class = Alunos_atualiza
    #form_class = Turma_form
    template_name = 'Escola/inicio.html'
    
    def get_success_url(self):
        aluno_id = self.object.id 
        return reverse_lazy('Gestao_Escolar:alunos_perfil', kwargs={'pk': aluno_id})  
    
    def form_valid(self, form):        
        data_nascimento = form.cleaned_data['data_nascimento']
        ano_atual = date.today().year
        idade = ano_atual - data_nascimento.year - ((ano_atual, data_nascimento.month, data_nascimento.day) < (ano_atual, date.today().month, date.today().day))
        form.instance.idade = idade    
        aluno = form.instance.nome_completo
        messages.success(self.request, f"Parabéns! As informações do aluno {aluno} foram atualizadas com sucesso!") 
        return super().form_valid(form)


    def get_context_data(self, **kwargs):
        svg = '<i class="fa-sharp fa-solid fa-people fs-5"></i>'
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Atualização do cadastro do aluno'          
        context['svg'] = svg 
        context['button'] = "Atualizar cadastro de "
        context['Alunos'] = Alunos.objects.all()
        context['now'] = datetime.now()
        context['update'] = "update"        
        context['conteudo_page'] = 'Registrar Alunos'     
        context['sub_Info_page'] = "Preencha os próximos campos para atualizar o cadastro do aluno"
        context['sub_Info_page_h4'] = "INFORMAÇÕES BÁSICAS DO ALUNO"       
        context['oculta_tab'] = "true"
        context['table'] = True   
        context['bottom'] = "Salvar Informações Básicas"            
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."  
        return context
    


