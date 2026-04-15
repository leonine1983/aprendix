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
    paginate_by = 3


   


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
    

# ─────────────────────────────────────────────
#  VIEW  ·  CardapioDetailView
#  Arquivo: merendaEscolar/views.py  (trecho)
# ─────────────────────────────────────────────

from django.views.generic import DetailView
from django.utils import timezone
from ...models import Cardapio, CardapioSemana, CardapioDia, CardapioItem


class CardapioDetailView(NutricionistaRequiredMixin, DetailView):
    """
    Exibe o detalhamento completo de um cardápio institucional.

    Contexto extra injetado:
    - dia_atual  : número do dia da semana (1=Seg … 5=Sex) para destacar "Hoje"
    - total_semanas  : quantidade de semanas do cardápio
    - total_dias     : total de dias cadastrados (todas as semanas)
    - total_refeicoes: total de itens cadastrados (todas as semanas/dias)
    """

    model = Cardapio
    template_name = "merendaEscolar/cardapio/cardapio_detail.html"
    context_object_name = "cardapio"

    def get_queryset(self):
        """
        Prefetch encadeado para evitar N+1 queries:
        cardapio → semanas → dias → itens (tipo_refeicao + receita)
        """
        from django.db.models import Prefetch
       
        return (
            Cardapio.objects
            .prefetch_related(
                Prefetch(
                    "semanas",
                    queryset=CardapioSemana.objects.order_by("numero").prefetch_related(
                        Prefetch(
                            "dias",
                            queryset=CardapioDia.objects.order_by("dia_semana").prefetch_related(
                                Prefetch(
                                    "itens",
                                    queryset=CardapioItem.objects
                                    .select_related("tipo_refeicao", "receita")
                                    .order_by("ordem"),
                                )
                            ),
                        )
                    ),
                )
            )
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cardapio = self.object

        # Dia atual (1=Seg, 7=Dom) para marcar "Hoje" no template
        hoje = timezone.now().isoweekday()          # 1=Seg … 7=Dom
        ctx["dia_atual"] = hoje if hoje <= 5 else None   # só úteis

        # Estatísticas do cardápio
        semanas = list(cardapio.semanas.all())
        ctx["total_semanas"] = len(semanas)

        total_dias = 0
        total_refeicoes = 0
        for semana in semanas:
            dias = list(semana.dias.all())
            total_dias += len(dias)
            for dia in dias:
                total_refeicoes += len(list(dia.itens.all()))

        ctx["total_dias"] = total_dias
        ctx["total_refeicoes"] = total_refeicoes

        return ctx

    



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
    template_name = "merendaEscolar/cardapio/tipo_refeição/tipo_refeicao_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Tipo atualizado!")
        return super().form_valid(form)


from django.shortcuts import get_object_or_404
from django.urls import reverse

class TipoRefeicaoDeleteView(NutricionistaRequiredMixin, DeleteView):
    model = TipoRefeicao
    success_url = reverse_lazy("merendaEscolar:tipo_refeicao_list")
    template_name = "merendaEscolar/cardapio/tipo_refeição/tiporefeicao_confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        
        # Verificar vínculos existentes com URLs
        vinculos = []
        
        # Verifica vínculos com CardapioItem
        itens_cardapio = obj.cardapioitem_set.select_related(
            'dia__semana__cardapio', 'receita'
        ).all()
        
        if itens_cardapio.exists():
            detalhes = []
            for item in itens_cardapio[:5]:  # Pega os 5 primeiros
                detalhes.append({
                    'objeto': item,
                    'texto': f"{item.receita.nome} - {item.dia.get_dia_semana_display()}",
                    'url': reverse('merendaEscolar:cardapio_detail', 
                                 kwargs={'pk': item.dia.semana.cardapio.pk})
                })
            
            vinculos.append({
                'tipo': 'Itens de Cardápio',
                'quantidade': itens_cardapio.count(),
                'detalhes': detalhes,
                'listagem_url': reverse('merendaEscolar:cardapio_list'),
                'icone': '📅'
            })
        
        context['tem_vinculos'] = len(vinculos) > 0
        context['vinculos'] = vinculos
        return context

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

class CardapioEscolaListView(NutricionistaRequiredMixin, ListView):
    model = CardapioEscola
    template_name = "merendaEscolar/cardapioEscola/cardapio_escola_list.html"
    context_object_name = "vinculos"
    paginate_by = 2  # Exibe 20 vínculos por página (ajuste conforme necessidade)


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
    template_name = "merendaEscolar/cardapioEscola/cardapio_escola_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Vínculo removido!")
        return super().delete(request, *args, **kwargs)