from django.views.generic import ListView
from admin_acessos.models import NotificacaoProduto
from django.contrib.auth.mixins import LoginRequiredMixin


class NotificacaoListView(LoginRequiredMixin, ListView):
    model = NotificacaoProduto
    template_name = "notificacoes/lista.html"
    context_object_name = "notificacoes"

    def get_queryset(self):
        return NotificacaoProduto.objects.filter(usuario=self.request.user)