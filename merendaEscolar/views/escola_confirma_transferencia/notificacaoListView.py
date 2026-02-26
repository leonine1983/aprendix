from django.views.generic import ListView
from admin_acessos.models import Notificacao
from django.contrib.auth.mixins import LoginRequiredMixin


class NotificacaoListView(LoginRequiredMixin, ListView):
    model = Notificacao
    template_name = "notificacoes/lista.html"
    context_object_name = "notificacoes"

    def get_queryset(self):
        return Notificacao.objects.filter(usuario=self.request.user)