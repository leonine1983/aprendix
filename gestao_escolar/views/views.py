from django.shortcuts import render, redirect
from gestao_escolar.models import *
from django.views.generic import ListView, TemplateView
from rh.models import Escola,Encaminhamentos
from gestao_escolar.models import  AnoLetivo, Alunos, Turmas
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


class Pagina_inicio(LoginRequiredMixin, TemplateView):
    model = Escola
    template_name = 'Escola/inicio.html'

    def get(self, request, *args, **kwargs):
        if 'escola_id' in request.session: 
                return super().get(request, *args, **kwargs)
        else:
            # Se a sessão é falsa, redirecione para a página desejada
            return redirect('Gestao_Escolar:GE_inicio')

    def get_context_data(self, **kwargs):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48"><path d="M38-160v-94q0-35 18-63.5t50-4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM9-103.5T622-423q69 8 130 23.5t99 35.5q33 19 52 47t19 63v94H738ZM358-481q-66 0-108-4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM94B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM90 108 4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM96-23 21t-9 31v34Zm260-321q39 0 64.5-25.5T448-631q0-39-25.5-64.5T358-721q-39 0-64.5 25.5T268-631q0 39 25.5 64.5T358-541Zm0 321Zm0-411Z"/></svg>'
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Selecione o ano letivo'                   
        context['svg'] = svg 
        context['now'] = datetime.now()        
        context['conteudo_page'] = 'info_escola'   
        # Corrigir o acesso ao objeto request
        sessao_escola = self.request.session['escola_id']
        context['contexto'] = Escola.objects.filter(id=sessao_escola)           
        context['condicional_aluno'] = Alunos.objects.all()
        context['condicional_professor'] = Encaminhamentos.objects.all()        
        context['condicional_turma'] = Turmas.objects.filter(escola = self.request.session['escola_id'], ano_letivo = self.request.session['anoLetivo_id'])       
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."
        
        return context

