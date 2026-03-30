from django.urls import reverse_lazy
from django.views.generic import *
from ...models import Cardapio, CardapioSemana, CardapioEscola, CardapioItem, CardapioDia
from core.permissions import GroupRequiredMixin
from core.groups.nutricionista import NUTRICIONISTA_GROUPS


# =========================
# CARDÁPIO
# =========================

class CardapioListView(GroupRequiredMixin, ListView):
    model = Cardapio
    template_name = "merendaEscolar/cardapio/cardapio_list.html"
    context_object_name = "cardapios"
    group_required = NUTRICIONISTA_GROUPS

    def get_queryset(self):
        return Cardapio.objects.order_by("-data_inicio")


class CardapioCreateView(GroupRequiredMixin, CreateView):
    model = Cardapio
    fields = ["nome", "descricao", "data_inicio", "data_fim", "ativo", "gerar_execucao"]
    template_name = "merendaEscolar/cardapio/cardapio_form.html"
    success_url = reverse_lazy("merendaEscolar:cardapio_list")
    group_required = NUTRICIONISTA_GROUPS

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        return super().form_valid(form)


class CardapioDetailView(GroupRequiredMixin, DetailView):
    model = Cardapio
    template_name = "merendaEscolar/cardapio/cardapio_detail.html"
    context_object_name = "cardapio"
    group_required = NUTRICIONISTA_GROUPS


class CardapioUpdateView(GroupRequiredMixin, UpdateView):
    model = Cardapio
    fields = ["nome", "descricao", "data_inicio", "data_fim", "ativo", "gerar_execucao"]
    template_name = "merendaEscolar/cardapio/cardapio_form.html"
    success_url = reverse_lazy("merendaEscolar:cardapio_list")
    group_required = NUTRICIONISTA_GROUPS


class CardapioDeleteView(GroupRequiredMixin, DeleteView):
    model = Cardapio
    template_name = "merendaEscolar/cardapio/cardapio_confirm_delete.html"
    success_url = reverse_lazy("merendaEscolar:cardapio_list")
    group_required = NUTRICIONISTA_GROUPS


# =========================
# SEMANA
# =========================

class SemanaCreateView(GroupRequiredMixin, CreateView):
    model = CardapioSemana
    fields = ["numero"]
    template_name = "merendaEscolar/cardapio/form/semana_form copy.html"
    group_required = NUTRICIONISTA_GROUPS

    def form_valid(self, form):
        cardapio = Cardapio.objects.get(pk=self.kwargs["cardapio_id"])
        form.instance.cardapio = cardapio
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("merendaEscolar:cardapio_detail", kwargs={"pk": self.object.cardapio.pk})


# =========================
# DIA
# =========================

class DiaCreateView(GroupRequiredMixin, CreateView):
    model = CardapioDia
    fields = ["dia_semana"]
    template_name = "merendaEscolar/cardapio/form/dia_form.html"
    group_required = NUTRICIONISTA_GROUPS

    def form_valid(self, form):
        semana = CardapioSemana.objects.get(pk=self.kwargs["semana_id"])
        form.instance.semana = semana
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("merendaEscolar:cardapio_detail", kwargs={"pk": self.object.semana.cardapio.pk})


# =========================
# ITEM
# =========================

class ItemCreateView(GroupRequiredMixin, CreateView):
    model = CardapioItem
    fields = ["tipo_refeicao", "receita", "ordem"]
    template_name = "merendaEscolar/cardapio/form/item_form.html"
    group_required = NUTRICIONISTA_GROUPS

    def form_valid(self, form):
        dia = CardapioDia.objects.get(pk=self.kwargs["dia_id"])
        form.instance.dia = dia
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("merendaEscolar:cardapio_detail", kwargs={"pk": self.object.dia.semana.cardapio.pk})