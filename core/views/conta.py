# core/views/conta.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.views import PasswordChangeView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy

from core.views.baseNutricionista import BaseNutricionistaView
from core.forms.perfil import PerfilForm
from core.models.perfil import PerfilUsuario


class MeuPerfilView(BaseNutricionistaView, UpdateView):
    """
    Exibe e edita o perfil do usuário autenticado.

    • GET  → mostra o template com os dados atuais
    • POST → salva dados do PerfilUsuario + User (via PerfilForm)

    Após POST com sucesso redireciona de volta para a mesma página.
    O template detecta `?tab=editar` na query string para reabrir
    a aba de edição caso venha de um redirecionamento.
    """

    model = PerfilUsuario
    form_class = PerfilForm
    template_name = "core/conta/meu_perfil.html"
    success_url = reverse_lazy("core:meu-perfil")

    # ── Garante que o perfil existe antes de renderizar ──────────────
    def get_object(self, queryset=None):
        perfil, _ = PerfilUsuario.objects.get_or_create(user=self.request.user)
        return perfil

    # ── Injeta o user no form para salvar first_name / last_name / email ──
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Perfil atualizado com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Corrija os erros abaixo e tente novamente.")
        # Reabre a aba de edição ao renderizar o template com erros
        return self.render_to_response(self.get_context_data(form=form, open_tab="editar"))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Passa a aba que deve estar aberta no carregamento
        ctx["open_tab"] = kwargs.get("open_tab", "visao-geral")
        return ctx


class AlterarSenhaView(LoginRequiredMixin, PasswordChangeView):
    template_name = "core/conta/alterar_senha.html"
    success_url = reverse_lazy("core:meu-perfil")

    def form_valid(self, form):
        messages.success(self.request, "Senha alterada com sucesso.")
        return super().form_valid(form)


class SairView(LoginRequiredMixin, LogoutView):
    next_page = reverse_lazy("login")

    def post(self, request, *args, **kwargs):
        messages.success(request, "Sessão encerrada com segurança.")
        return super().post(request, *args, **kwargs)


class ConfiguracoesView(LoginRequiredMixin, TemplateView):
    template_name = "core/conta/configuracoes.html"