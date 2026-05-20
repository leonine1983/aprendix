# merendaEscolar/views/configuracao.py

from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages

from core.models import ConfiguraPessoal
from core.views.baseNutricionista import BaseNutricionistaView


class ConfiguracaoPessoalUpdateView(BaseNutricionistaView, UpdateView):
    model = ConfiguraPessoal

    # Excluímos o campo "usuario" do formulário, pois ele será
    # preenchido automaticamente com request.user.
    exclude = ["usuario"]

    template_name = "merendaEscolar/configuraSistem/configuraPessoal.html"

    def get_success_url(self):
        next_url = self.request.POST.get("next")
        if next_url:
            return next_url
        return reverse_lazy("merendaEscolar:configuracao_pessoal")

    def get_object(self, queryset=None):
        """
        Retorna a configuração do usuário logado.

        Se ainda não existir, cria automaticamente com os valores
        padrão definidos no model ConfiguraPessoal.
        """
        obj, created = ConfiguraPessoal.objects.get_or_create(
            usuario=self.request.user
        )
        return obj

    def form_valid(self, form):
        """
        Garante que o usuário logado seja salvo no campo usuario.
        Isso é importante principalmente no primeiro acesso,
        quando o registro é criado automaticamente.
        """
        form.instance.usuario = self.request.user

        messages.success(
            self.request,
            "Configuração atualizada com sucesso."
        )

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Erro ao atualizar configuração. Verifique os dados."
        )
        return super().form_invalid(form)