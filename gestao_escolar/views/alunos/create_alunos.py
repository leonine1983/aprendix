from gestao_escolar.models import Alunos
from django.http import HttpResponseBadRequest
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from datetime import datetime, date
from django.urls import reverse_lazy
from .alunos_form import *
from django.db.models import Q
from django.shortcuts import redirect


class Create_Alunos(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Alunos
    form_class = Alunos_form
    template_name = 'Escola/inicio.html'
    success_message = "Aluno registrado com sucesso!!"
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')

    def get_success_url(self):
        aluno_id = self.object.id 
        return reverse_lazy('Gestao_Escolar:alunos_create_etapa2', kwargs={'pk': aluno_id})  

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
        context['sub_Info_page'] = 'Antes de procedermos com o cadastro do aluno,\
              é imprescindível realizar uma verificação para confirmar se ele já está\
                  registrado no sistema. Essa medida visa evitar duplicatas e garantir a\
                      integridade dos dados.' 
        aluno_query = self.get_queryset()                
        context['Alunos'] = aluno_query
        context['now'] = datetime.now()    
        context['bottom'] = 'Avançar'          
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."        
        return context   
    
    def form_valid(self, form):
        # Verifica se já existe um aluno com o mesmo nome
        nome_completo = form.cleaned_data['nome_completo']
        nome_mae = form.cleaned_data['nome_mae']        
        #if Alunos.objects.filter(nome_completo__iexact=nome_completo).exists():
        if Alunos.objects.filter(nome_completo__icontains=nome_completo, nome_mae__icontains = nome_mae).exists():
            return redirect('Gestao_Escolar:alunos_encontred', nome_completo=nome_completo, nome_mae=nome_mae)
        if self.request.user.first_name:        
            form.instance.res_cadastro = f'{self.request.user.first_name} {self.request.user.last_name}'
        else:
            form.instance.res_cadastro = self.request.user        
        return super().form_valid(form)
    