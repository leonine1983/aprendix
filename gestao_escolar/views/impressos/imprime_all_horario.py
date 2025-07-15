from typing import Any
from django.views.generic import ListView
from rh.models import Escola, Ano
from gestao_escolar.models import Turmas, Horario

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin


class ImprimeAllHorarios (LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Horario
    template_name = 'Escola/inicio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ano = self.request.session['anoLetivo_id']
        escola = self.request.session['escola_id']
        escolas = Escola.objects.get(pk=escola)
        ano_l = Ano.objects.get(id=ano)
        horario = Horario.objects.filter(turma__escola = escolas, turma__ano_letivo = ano_l)
        turmas = Turmas.objects.filter(ano_letivo=ano, escola = escola)
        context ['list_turmas'] = turmas
        context ['horarios'] = horario
        context ['conteudo_page'] = "imprime_all_horario"        
        
        return context

