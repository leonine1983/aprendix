from gestao_escolar.models import Alunos
from django.http import HttpResponseBadRequest
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from datetime import datetime, date
from django.urls import reverse_lazy
from gestao_escolar.views.alunos.alunos_form import Alunos_form
from django.db.models import Q
from django.shortcuts import redirect


class CreateAlunosConfirma(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Alunos
    form_class = Alunos_form
    #form_class = Turma_form
    template_name = 'Escola/inicio.html'
    success_message = "Aluno registrado com sucesso!!"

    def get_success_url(self):
        # Obtém o ID do registro criado
        aluno_id = self.object.id 

        # Redireciona para a nova view com o ID do aluno
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
