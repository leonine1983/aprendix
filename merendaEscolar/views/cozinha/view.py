from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.contrib import messages
from ...models import (
    Cardapio, CardapioSemana, CardapioDia,
    TipoRefeicao, CardapioItem, CardapioEscola
)
from core.groups.nutricionista import NutricionistaRequiredMixin
from django.core.exceptions import ValidationError


from django import forms

class CardapioForm(forms.ModelForm):
    class Meta:
        model = Cardapio
        fields = [
            "nome",
            "descricao",
            "data_inicio",
            "data_fim",
            "ativo",
            "gerar_execucao",
        ]
        widgets = {
            "data_inicio": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "data_fim": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }


class CardapioListView(NutricionistaRequiredMixin, ListView):
    model = Cardapio
    template_name = "merendaEscolar/cardapio/cardapio_list.html"

   


class CardapioCreateView(NutricionistaRequiredMixin, CreateView):
    model = Cardapio
    form_class = CardapioForm
    template_name = "merendaEscolar/cardapio/cardapio_form.html"
    success_url = reverse_lazy("merendaEscolar:cardapio_list")

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        messages.success(self.request, "Cardápio criado com sucesso!")
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        messages.error(self.request, "Erro ao salvar. Verifique os campos.")
        return super().form_invalid(form)


class CardapioUpdateView(NutricionistaRequiredMixin, UpdateView):
    model = Cardapio
    form_class = CardapioForm
    success_url = reverse_lazy("merendaEscolar:cardapio_list")
    template_name = "merendaEscolar/cardapio/cardapio_form.html"


    def form_valid(self, form):
        messages.success(self.request, "Cardápio atualizado com sucesso!")
        return super().form_valid(form)


class CardapioDeleteView(NutricionistaRequiredMixin, DeleteView):
    model = Cardapio
    success_url = reverse_lazy("merendaEscolar:cardapio_list")
    template_name = "merendaEscolar/cardapio/cardapio_confirm_delete.html"   

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Cardápio removido com sucesso!")
        return super().delete(request, *args, **kwargs)


# =========================
# SEMANA
# =========================


from django.shortcuts import get_object_or_404

class SemanaCreateView(NutricionistaRequiredMixin, CreateView):
    model = CardapioSemana
    fields = ['numero']
    success_url = reverse_lazy("merendaEscolar:cardapio_list")
    template_name = "merendaEscolar/cardapio/form/semana_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.cardapio = get_object_or_404(Cardapio, pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial["cardapio"] = self.cardapio
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)       

        # 🔥 já define o valor
        form.instance.cardapio = self.cardapio

        return form

    def form_valid(self, form):
        form.instance.cardapio = self.cardapio  # segurança extra

        messages.success(self.request, "Semana adicionada com sucesso!")
        return super().form_valid(form)


class SemanaUpdateView(NutricionistaRequiredMixin, UpdateView):
    model = CardapioSemana
    fields = ['numero']
    success_url = reverse_lazy("merendaEscolar:cardapio_list")
    template_name = "merendaEscolar/cardapio/form/semana_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Semana atualizada!")
        return super().form_valid(form)


class SemanaDeleteView(DeleteView):
    model = CardapioSemana
    success_url = reverse_lazy("merendaEscolar:cardapio_list")
    template_name = "merendaEscolar/cardapio/form/semana_form.html"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Semana removida!")
        return super().delete(request, *args, **kwargs)


# =========================
# DIA
# =========================
class DiaCreateView(NutricionistaRequiredMixin, CreateView):
    model = CardapioDia
    fields = ['dia_semana']
    success_url = reverse_lazy("merendaEscolar:cardapio_list")
    template_name = "merendaEscolar/cardapio/form/dia_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.semana = get_object_or_404(CardapioSemana, pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_initial(self):
        initial = super().get_initial()
        initial['semana'] = self.semana
        return initial
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.instance.semana = self.semana
        return form

    def form_valid(self, form):
        messages.success(self.request, "Dia criado com sucesso!")
        return super().form_valid(form)


class DiaUpdateView(NutricionistaRequiredMixin, UpdateView):
    model = CardapioDia
    fields = "__all__"
    success_url = reverse_lazy("merendaEscolar:cardapio_list")
    template_name = "merendaEscolar/cardapio/form/dia_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Dia atualizado!")
        return super().form_valid(form)


class DiaDeleteView(NutricionistaRequiredMixin, DeleteView):
    model = CardapioDia
    success_url = reverse_lazy("merendaEscolar:cardapio_list")
    template_name = "merendaEscolar/cardapio/form/dia_form.html"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Dia removido!")
        return super().delete(request, *args, **kwargs)


# =========================
# TIPO REFEICAO
# =========================

class TipoRefeicaoListView(NutricionistaRequiredMixin, ListView):
    model = TipoRefeicao
    template_name = "merendaEscolar/cardapio/tipo_refeição/tipo_refeicao_list.html"


class TipoRefeicaoCreateView(NutricionistaRequiredMixin, CreateView):
    model = TipoRefeicao
    fields = "__all__"
    success_url = reverse_lazy("merendaEscolar:tipo_refeicao_list")
    template_name = "merendaEscolar/cardapio/tipo_refeição/tipo_refeicao_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Tipo de refeição criado!")
        return super().form_valid(form)


class TipoRefeicaoUpdateView(NutricionistaRequiredMixin, UpdateView):
    model = TipoRefeicao
    fields = "__all__"
    success_url = reverse_lazy("merendaEscolar:tipo_refeicao_list")

    def form_valid(self, form):
        messages.success(self.request, "Tipo atualizado!")
        return super().form_valid(form)


class TipoRefeicaoDeleteView(NutricionistaRequiredMixin, DeleteView):
    model = TipoRefeicao
    success_url = reverse_lazy("merendaEscolar:tipo_refeicao_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Tipo removido!")
        return super().delete(request, *args, **kwargs)


# =========================
# ITEM
# =========================

from django.shortcuts import get_object_or_404

from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.views.generic import CreateView

from merendaEscolar.models import CardapioItem, CardapioDia


class ItemCreateView(NutricionistaRequiredMixin, CreateView):
    model = CardapioItem
    fields = ["tipo_refeicao", "receita", "ordem"]
    template_name = "merendaEscolar/cardapio/form/item_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.dia = get_object_or_404(CardapioDia, pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.dia = self.dia

        tipo = form.cleaned_data.get("tipo_refeicao")
        ordem = form.cleaned_data.get("ordem")
        receita = form.cleaned_data.get("receita")

        # 🔹 1. Validar ORDEM duplicada
        if CardapioItem.objects.filter(
            dia=self.dia,
            tipo_refeicao=tipo,
            ordem=ordem
        ).exists():
            form.add_error("ordem", "Já existe um item com essa ordem para esse tipo de refeição.")
            return self.form_invalid(form)

        # 🔹 2. Validar RECEITA duplicada
        if CardapioItem.objects.filter(
            dia=self.dia,
            tipo_refeicao=tipo,
            receita=receita
        ).exists():
            form.add_error("receita", "Essa receita já foi adicionada para esse tipo de refeição neste dia.")
            return self.form_invalid(form)

        messages.success(self.request, "Item adicionado com sucesso!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Erro ao adicionar item. Verifique os campos abaixo.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dia"] = self.dia

        # 🔥 EXTRA UX: mostrar itens já cadastrados
        context["itens_existentes"] = CardapioItem.objects.filter(
            dia=self.dia
        ).select_related("tipo_refeicao", "receita").order_by("tipo_refeicao", "ordem")

        return context


class ItemUpdateView(NutricionistaRequiredMixin, UpdateView):
    model = CardapioItem
    fields = "__all__"
    success_url = reverse_lazy("merendaEscolar:cardapio_list")

    def form_valid(self, form):
        messages.success(self.request, "Item atualizado!")
        return super().form_valid(form)


class ItemDeleteView(NutricionistaRequiredMixin, DeleteView):
    model = CardapioItem
    success_url = reverse_lazy("merendaEscolar:cardapio_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Item removido!")
        return super().delete(request, *args, **kwargs)


# =========================
# CARDAPIO ESCOLA
# =========================

# =========================
# CARDAPIO ESCOLA LIST
# =========================
class CardapioEscolaListView(NutricionistaRequiredMixin, ListView):
    model = CardapioEscola
    template_name = "merendaEscolar/cardapioEscola/cardapio_escola_list.html"
    context_object_name = "vinculos"


class CardapioEscolaCreateView(NutricionistaRequiredMixin, CreateView):
    model = CardapioEscola
    fields = "__all__"
    success_url = reverse_lazy("merendaEscolar:cardapio_escola_list")
    template_name = "merendaEscolar/cardapioEscola/cardapio_escola_create.html"

    def form_valid(self, form):
        cardapio = form.cleaned_data["cardapio"]
        escola = form.cleaned_data["escola"]

        if CardapioEscola.objects.filter(cardapio=cardapio, escola=escola).exists():
            form.add_error(None, "Esse vínculo já existe.")
            return self.form_invalid(form)

        messages.success(self.request, "Cardápio vinculado à escola!")
        return super().form_valid(form)
    

import csv
from django.shortcuts import redirect
from django.contrib import messages

class CardapioEscolaUploadView(NutricionistaRequiredMixin, View):

    def post(self, request):
        arquivo = request.FILES.get("arquivo")

        if not arquivo:
            messages.error(request, "Envie um arquivo CSV.")
            return redirect("merendaEscolar:cardapio_escola_list")

        decoded = arquivo.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded)

        criados = 0
        ignorados = 0

        for row in reader:
            cardapio_id = row.get("cardapio_id")
            escola_id = row.get("escola_id")

            if not cardapio_id or not escola_id:
                continue

            obj, created = CardapioEscola.objects.get_or_create(
                cardapio_id=cardapio_id,
                escola_id=escola_id
            )

            if created:
                criados += 1
            else:
                ignorados += 1

        messages.success(request, f"{criados} criados, {ignorados} ignorados.")
        return redirect("merendaEscolar:cardapio_escola_list")


class CardapioEscolaDeleteView(NutricionistaRequiredMixin, DeleteView):
    model = CardapioEscola
    success_url = reverse_lazy("merendaEscolar:cardapio_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Vínculo removido!")
        return super().delete(request, *args, **kwargs)