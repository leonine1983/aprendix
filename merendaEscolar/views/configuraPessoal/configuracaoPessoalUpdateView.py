# merendaEscolar/views/configuracao.py

from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages

from core.models import ConfiguraPessoal
from core.views.baseNutricionista import BaseNutricionistaView


class ConfiguracaoPessoalUpdateView(BaseNutricionistaView, UpdateView):
    model = ConfiguraPessoal
    fields =  '__all__'
    template_name = "merendaEscolar/configuraSistem/configuraPessoal.html"
    # success_url = reverse_lazy("merendaEscolar:configuracao_pessoal")

    def get_success_url(self):
        next_url = self.request.POST.get("next")
        if next_url:
            return next_url
        return reverse_lazy("merendaEscolar:configuracao_pessoal")

    def get_object(self, queryset=None):
        """
        🔒 Garante que sempre exista UMA configuração global
        """
        obj, _ = ConfiguraPessoal.objects.get_or_create(pk=1)
        return obj

    def form_valid(self, form):
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