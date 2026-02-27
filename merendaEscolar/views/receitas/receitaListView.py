from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages

from core.groups.nutricionista import NUTRICIONISTA_GROUPS
from core.permissions import GroupRequiredMixin

from ...models import Receita


class ReceitaListView(
    LoginRequiredMixin,
    GroupRequiredMixin,
    PermissionRequiredMixin,
    ListView
):
    model = Receita
    template_name = "merendaEscolar/receitas/receita_lista.html"
    context_object_name = "receitas"
    paginate_by = 20

    permission_required = "merendaEscolar.view_receita"
    group_required = NUTRICIONISTA_GROUPS


class ReceitaDetailView(
    LoginRequiredMixin,
    GroupRequiredMixin,
    PermissionRequiredMixin,
    DetailView
):
    model = Receita
    template_name = "merendaEscolar/receitas/receitar_detalhe.html"
    context_object_name = "receita"

    permission_required = "merendaEscolar.view_receita"
    group_required = NUTRICIONISTA_GROUPS


class ReceitaCreateView(
    LoginRequiredMixin,
    GroupRequiredMixin,
    PermissionRequiredMixin,
    CreateView
):
    model = Receita
    fields = ["nome", "descricao", "modo_preparo", "ativa"]
    template_name = "merendaEscolar/receitas/receita_form.html"
    success_url = reverse_lazy("merendaEscolar:receita_lista")

    permission_required = "merendaEscolar.add_receita"
    group_required = NUTRICIONISTA_GROUPS

    def form_valid(self, form):
        form.instance.criada_por = self.request.user
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Receita institucional cadastrada com sucesso."
        )

        return response


class ReceitaUpdateView(
    LoginRequiredMixin,
    GroupRequiredMixin,
    PermissionRequiredMixin,
    UpdateView
):
    model = Receita
    fields = ["nome", "descricao", "modo_preparo", "ativa"]
    template_name = "merendaEscolar/receitas/receita_form.html"
    success_url = reverse_lazy("merendaEscolar:receita_lista")

    permission_required = "merendaEscolar.change_receita"
    group_required = NUTRICIONISTA_GROUPS

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Receita institucional atualizada com sucesso."
        )

        return response


class ReceitaDeleteView(
    LoginRequiredMixin,
    GroupRequiredMixin,
    PermissionRequiredMixin,
    DeleteView
):
    model = Receita
    template_name = "merendaEscolar/receitas/receita_excluir.html"
    success_url = reverse_lazy("merendaEscolar:receita_lista")

    permission_required = "merendaEscolar.delete_receita"
    group_required = NUTRICIONISTA_GROUPS

    def form_valid(self, form):
        messages.success(
            self.request,
            "Receita institucional excluída com sucesso."
        )
        return super().form_valid(form)