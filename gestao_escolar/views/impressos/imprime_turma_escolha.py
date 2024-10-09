from typing import Any
from django.views.generic import ListView
from rh.models import Escola
from gestao_escolar.models import Turmas

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

"""
class ImprimeTurmasFiltros (LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Turmas
    template_name = 'Escola/inicio.html'



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ano = self.request.session['anoLetivo_id']
        escola = self.request.session['escola_id']
        escolas = Escola.objects.get(pk=escola)
        turmas = Turmas.objects.filter(ano_letivo=ano, escola = escola)
        context ['list_turmas'] = turmas
        context ['list_escola'] = escolas
        context ['conteudo_page'] = "imprime_turma_filtros"        
        
        return context
    
"""
class ImprimeTurmasFiltros(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Turmas
    template_name = 'Escola/inicio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ano = self.request.session['anoLetivo_id']
        escola = self.request.session['escola_id']
        escolas = Escola.objects.get(pk=escola)
        turmas = Turmas.objects.filter(ano_letivo=ano, escola=escola)

        # Criar um dicionário para armazenar as contagens de camisas
        for turma in turmas:
            camisa_counts = {
                'PP': turma.related_matricula_turma.filter(camisa_tamanho__nome='PP').count(),
                'P': turma.related_matricula_turma.filter(camisa_tamanho__nome='P').count(),
                'M': turma.related_matricula_turma.filter(camisa_tamanho__nome='M').count(),
                'G': turma.related_matricula_turma.filter(camisa_tamanho__nome='G').count(),
                'GG': turma.related_matricula_turma.filter(camisa_tamanho__nome='GG').count(),
            }            
            turma.camisa_counts = camisa_counts
            """_gte = maior ou igual a
                __lt = menor que"""
            idade_counts = {
                'ate_11': turma.related_matricula_turma.filter(aluno__idade__lt=11).count(),
                'maior_11_e_menor_18': turma.related_matricula_turma.filter(aluno__idade__gte=11, aluno__idade__lt=18).count(),
                'maior_igual_18': turma.related_matricula_turma.filter(aluno__idade__gte=18).count(),
            }
            turma.idade_counts = idade_counts

        context['list_turmas'] = turmas
        context['list_escola'] = escolas
        context['conteudo_page'] = "imprime_turma_filtros"
        
        return context
