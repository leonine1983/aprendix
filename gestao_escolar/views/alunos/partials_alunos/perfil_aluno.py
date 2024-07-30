from gestao_escolar.models import Alunos
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from datetime import  date
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import redirect
from gestao_escolar.views.alunos.aluno_form.alun_5_forms import Alunos_form_etapa5

class PerfilAluno(LoginRequiredMixin, SuccessMessageMixin, DetailView):
    model = Alunos
    template_name = 'Escola/inicio.html' 


    def get_queryset(self):
        txt_nome = self.request.GET.get('busca-aluno')
        if txt_nome:
            Aluno = Alunos.objects.filter(Q(nome_completo__icontains = txt_nome) )
        else:
            Aluno = Alunos.objects.all()        
        return Aluno

    def get_context_data(self, **kwargs):        
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Alunos'   
        context['sub_titulo_page'] = 'Perfil do Aluno'         
        context['conteudo_page'] = 'Registrar Alunos'            
        context['sub_Info_page'] = "Extra"
        context['sub_Info_page_h4'] = "INFORMAÇÕES EXTRA DO ALUNO"       
        context['oculta_tab'] = "true"
        context['table'] = True 
        context['bottom'] = "Salvar informações extras do aluno"      
        return context   
    
   