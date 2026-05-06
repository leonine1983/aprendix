# modulo_Merendeiras/views.py

from django.views.generic import TemplateView, ListView, DetailView, CreateView, View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Sum
from ..forms import ReceitaForm
from merendaEscolar.models import (
    Receita,
    ExecucaoReceita,
    EstoqueEscola,
)
from merendaEscolar.services import executar_receita


from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.db.models import Sum

# merendaEscolar/views/configuracao.py

from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages

from core.models import ConfiguraPessoal
from core.views.baseMerendeira import BaseMerendeiraView




# =========================
# DASHBOARD OPERACIONAL
# =========================





class DashboardMerendeiraView(BaseMerendeiraView, TemplateView):
    template_name = "modulo_merendeiras/dashboard_merendeira.html"

    def get_escola_usuario(self):
        """
        Recupera a escola vinculada ao usuário de forma segura.
        Evita quebra de sistema caso o perfil não exista.
        """
        perfil = getattr(self.request.user, "perfilusuario", None)

        if not perfil:
            messages.error(self.request, "Perfil de usuário não encontrado.")
            return None

        if not perfil.escola:
            messages.warning(self.request, "Usuário não está vinculado a nenhuma escola.")
            return None

        return perfil.escola

    def dispatch(self, request, *args, **kwargs):
        """
        Camada de proteção antes da execução da view.
        Evita processamento desnecessário e falhas internas.
        """
        escola = self.get_escola_usuario()

        if not escola:
            messages.warning(self.request, "O profissional não está vinculado a nenhuma escola")
            return redirect("admin_acessos:logout")  # ou página institucional adequada

        self.escola = escola
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        escola = self.escola

        # 🔥 Uso de aggregate direto no banco (performance e escalabilidade)
        ctx["total_itens"] = (
            EstoqueEscola.objects
            .filter(escola=escola)
            .aggregate(total=Sum("quantidade"))["total"] or 0
        )

        ctx["receitas_ativas"] = Receita.objects.filter(ativa=True).count()

        ctx["execucoes_hoje"] = (
            ExecucaoReceita.objects
            .filter(escola=escola)
            .count()
        )

        return ctx


# =========================
# ESTOQUE DA ESCOLA
# =========================

# =========================
# RECEITAS
# =========================

class ReceitaListView(BaseMerendeiraView, ListView):
    model = Receita
    template_name = "modulo_merendeiras/receita_lista.html"
    context_object_name = "receitas"

    def get_queryset(self):
        return Receita.objects.filter(ativa=True)


class ReceitaCreateView(BaseMerendeiraView, CreateView):
    model = Receita
    form_class = ReceitaForm
    template_name = "modulo_merendeiras/receita_form.html"
    success_url = reverse_lazy("modulo_merendeiras:receita_lista")

    def form_valid(self, form):
        form.instance.criada_por = self.request.user
        messages.success(self.request, "Receita cadastrada com sucesso.")
        return super().form_valid(form)


class ReceitaDetailView(BaseMerendeiraView, DetailView):
    model = Receita
    template_name = "modulo_merendeiras/receita_detalhe.html"


# =========================
# EXECUÇÃO DE RECEITA
# =========================

class ExecucaoListView(BaseMerendeiraView, ListView):
    model = ExecucaoReceita
    template_name = "modulo_merendeiras/execucao_lista.html"
    context_object_name = "execucoes"

    def get_queryset(self):
        return ExecucaoReceita.objects.filter(
            escola=self.request.user.escola
        )


class ExecutarReceitaView(BaseMerendeiraView, View):

    def post(self, request, pk):
        execucao = get_object_or_404(
            ExecucaoReceita,
            pk=pk,
            escola=request.user.escola
        )

        try:
            executar_receita(execucao, request.user)
            messages.success(request, "Receita executada e estoque atualizado.")
        except Exception as e:
            messages.error(request, str(e))

        return redirect("modulo_merendeiras:execucao_lista")
    






class ConfiguracaoPessoalUpdateView(BaseMerendeiraView, UpdateView):
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