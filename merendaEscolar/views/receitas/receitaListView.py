from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages

from core.groups.nutricionista import NUTRICIONISTA_GROUPS
from core.permissions import GroupRequiredMixin



from django.shortcuts import redirect
from django.forms import inlineformset_factory
from ...models import Receita, ReceitaIngrediente


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




# ajuste conforme seu projeto
NUTRICIONISTA_GROUPS = ("Nutricionista", "Admin")


# ==============================
# FORMSET DE INGREDIENTES
# ==============================
ReceitaIngredienteFormSet = inlineformset_factory(
    Receita,
    ReceitaIngrediente,
    fields=["produto", "quantidade"],
    extra=3,              # quantidade inicial de linhas
    can_delete=True
)


# ==============================
# CREATE VIEW COMPLETA
# ==============================
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

    # ==============================
    # CONTEXTO COM FORMSET
    # ==============================
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context["formset"] = ReceitaIngredienteFormSet(
                self.request.POST
            )
        else:
            context["formset"] = ReceitaIngredienteFormSet()

        return context

    # ==============================
    # SALVAMENTO COMPLETO
    # ==============================
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]

        # define usuário
        form.instance.criada_por = self.request.user

        # valida tudo junto
        if formset.is_valid():
            self.object = form.save()

            formset.instance = self.object
            formset.save()

            messages.success(
                self.request,
                "Receita institucional cadastrada com sucesso."
            )

            return redirect(self.success_url)

        # se formset inválido, renderiza novamente
        return self.render_to_response(
            self.get_context_data(form=form)
        )

    # ==============================
    # CASO FORM PRINCIPAL DÊ ERRO
    # ==============================
    def form_invalid(self, form):
        messages.error(
            self.request,
            "Erro ao cadastrar receita. Verifique os campos."
        )
        return super().form_invalid(form)

# Update das Receitas ----------------------------------------------------
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

    # ==============================
    # CONTEXTO COM FORMSET
    # ==============================
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context["formset"] = ReceitaIngredienteFormSet(
                self.request.POST,
                instance=self.object   # 🔥 ESSENCIAL
            )
        else:
            context["formset"] = ReceitaIngredienteFormSet(
                instance=self.object   # 🔥 CARREGA EXISTENTES
            )

        return context

    # ==============================
    # SALVAR TUDO JUNTO
    # ==============================
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]

        if formset.is_valid():
            self.object = form.save()

            formset.instance = self.object
            formset.save()

            messages.success(
                self.request,
                "Receita institucional atualizada com sucesso."
            )

            return redirect(self.success_url)

        return self.render_to_response(
            self.get_context_data(form=form)
        )

    # ==============================
    # ERRO
    # ==============================
    def form_invalid(self, form):
        messages.error(
            self.request,
            "Erro ao atualizar receita. Verifique os campos."
        )
        return super().form_invalid(form)




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