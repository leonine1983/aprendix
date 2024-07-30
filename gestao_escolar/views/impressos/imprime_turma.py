from typing import Any
from django.views.generic import ListView
from rh.models import Escola
from gestao_escolar.models import Turmas

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin


class Imprime_Turmas (LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Turmas
    template_name = 'Escola/inicio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ano = self.request.session['anoLetivo_id']
        escola = self.request.session['escola_id']
        escolas = Escola.objects.get(pk=escola)
        turmas = Turmas.objects.filter(ano_letivo=ano)
        context ['list_turmas'] = turmas
        context ['list_escola'] = escolas
        context ['conteudo_page'] = "imprime_turma"
        
        
        return context