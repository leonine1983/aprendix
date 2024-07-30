from rh.models import Profissao
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin


class Relacao_profissao(LoginRequiredMixin, ListView):
    model = Profissao
    template_name = 'rh/inicio.html'
    context_object_name = 'lista_profissoes'
