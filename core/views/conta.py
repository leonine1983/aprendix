from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.views import PasswordChangeView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model




User = get_user_model()


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.views import PasswordChangeView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from core.forms.perfil import PerfilForm
from core.models.perfil import PerfilUsuario


from django.shortcuts import get_object_or_404
from core.models.perfil import PerfilUsuario

class MeuPerfilView(LoginRequiredMixin, UpdateView):
    model = PerfilUsuario
    form_class = PerfilForm
    template_name = "core/conta/meu_perfil.html"
    success_url = reverse_lazy("core:meu-perfil")

    def get_object(self):
        perfil, created = PerfilUsuario.objects.get_or_create(
            user=self.request.user
        )
        return perfil

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Perfil atualizado com sucesso.")
        return super().form_valid(form)


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

