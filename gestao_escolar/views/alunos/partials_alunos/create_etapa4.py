from gestao_escolar.models import Alunos
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from datetime import  date
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import redirect
from gestao_escolar.views.alunos.aluno_form.alun_4_forms import Alunos_form_etapa4

class CreateAlunosConfirmaEtapa4(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Alunos
    form_class = Alunos_form_etapa4
    template_name = 'Escola/inicio.html'
    success_message = "Aluno registrado com sucesso!!"

    def get_success_url(self):
        aluno_id = self.object.id 
        return reverse_lazy('Gestao_Escolar:alunos_create_etapa5', kwargs={'pk': aluno_id})  


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
        context['conteudo_page'] = 'Registrar Alunos'            
        context['sub_Info_page'] = "Saúde do Aluno"
        context['sub_Info_page_h4'] = "INFORMAÇÕES ACERCA DA SAÚDE DO ALUNO"       
        context['oculta_tab'] = "true"
        context['table'] = True 
        context['bottom'] = "Salvar informações sobre a saúde do aluno"      
        return context   
    
   