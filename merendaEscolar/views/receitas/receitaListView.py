from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages

from core.groups.nutricionista import NUTRICIONISTA_GROUPS
from core.views.baseNutricionista import BaseNutricionistaView
from core.permissions import GroupRequiredMixin



from django.shortcuts import redirect
from django.forms import inlineformset_factory
from ...models import Receita, ReceitaIngrediente, CardapioItem, ExecucaoReceita
from core.models import ConfiguraPessoal

from django.db.models import Q

class ReceitaListView(BaseNutricionistaView, ListView):
    model = Receita
    template_name = "merendaEscolar/receitas/receita_lista.html"
    context_object_name = "receitas"  # Mantém compatibilidade com seu template            
    ordering = ['-criada_em']         # Ordenação padrão

    # Faz com o que os dados de configuração sejam carregados antes de todo o conteudo da view
    def dispatch(self, request, *args, **kwargs):
        self.configuracao, _ = ConfiguraPessoal.objects.get_or_create(pk=1)
        return super().dispatch(request, *args, **kwargs)

    # Define a quantidade de registros na tela
    def get_paginate_by(self, queryset):
        return self.configuracao.pagina_receitas  


    def get_queryset(self):
        queryset = super().get_queryset().select_related('criada_por')
        
        # Filtro de busca
        self.search_query = self.request.GET.get('q', '').strip()
        if self.search_query:
            queryset = queryset.filter(
                Q(nome__icontains=self.search_query) | 
                Q(descricao__icontains=self.search_query)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        # IMPORTANTE: Chamar super() primeiro para incluir page_obj no contexto
        context = super().get_context_data(**kwargs)
        
        # Preserva o termo de busca para o template
        context['search_query'] = getattr(self, 'search_query', '')
        
        # Contadores (usando count() no queryset completo, não apenas na página)
        base_qs = Receita.objects.all()
        if getattr(self, 'search_query', ''):
            base_qs = base_qs.filter(
                Q(nome__icontains=self.search_query) | 
                Q(descricao__icontains=self.search_query)
            )
            
        context['total_receitas'] = base_qs.count()
        context['receitas_ativas'] = base_qs.filter(ativa=True).count()
        context["pagina_transferencia"] = self.configuracao.pagina_receitas  
        # 🔷 Fonte única de verdade (governança)
        context["page_size_options"] = [10, 20, 30, 50]
        
        return context
    




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
    fields=['produto', 'quantidade'],
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
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
    fields = ["nome", "descricao", "modo_preparo", "ativa", 'rendimento']
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
                self.request.POST,
                prefix='ingredientes' 
            )
        else:
            context["formset"] = ReceitaIngredienteFormSet(
                prefix='ingredientes' 
            )

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
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.db import transaction

class ReceitaUpdateView(
    LoginRequiredMixin,
    GroupRequiredMixin,
    PermissionRequiredMixin,
    UpdateView
):
    model = Receita
    fields = ["nome", "descricao", "modo_preparo", "ativa", 'rendimento']
    template_name = "merendaEscolar/receitas/receita_form.html"
    success_url = reverse_lazy("merendaEscolar:receita_lista")

    permission_required = "merendaEscolar.change_receita"
    group_required = NUTRICIONISTA_GROUPS

    # ==============================
    # GARANTE OBJECT NO POST
    # ==============================
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    # ==============================
    # CONTEXTO COM FORMSET
    # ==============================
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context["formset"] = ReceitaIngredienteFormSet(
                self.request.POST,
                instance=self.object
            )
        else:
            context["formset"] = ReceitaIngredienteFormSet(
                instance=self.object
            )

        return context

    # ==============================
    # VALIDAÇÃO GLOBAL (FORM + FORMSET)
    # ==============================
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]

        if not formset.is_valid():
            return self.form_invalid(form)

        with transaction.atomic():
            # salva receita
            self.object = form.save()

            # vincula corretamente o formset
            formset.instance = self.object
            formset.save()

        messages.success(
            self.request,
            "Receita institucional atualizada com sucesso."
        )

        return redirect(self.success_url)

    # ==============================
    # TRATAMENTO DE ERRO
    # ==============================
    def form_invalid(self, form):
        messages.error(
            self.request,
            "Erro ao atualizar receita. Corrija os campos destacados."
        )
        return self.render_to_response(
            self.get_context_data(form=form)
        )




# DELETAR RECEITA --------------------   

from django.urls import reverse

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        receita = self.object
        bloqueios = []

        # 🔒 1. Execução de receita (uso real)
        execucoes = ExecucaoReceita.objects.filter(receita=receita)

        if execucoes.exists():
            for execucao in execucoes:
                bloqueios.append({
                    "tipo": "Execução de Receita",
                    "descricao": f"Execução na escola {execucao.escola}",
                    "url": "#",  # você pode criar uma rota futura
                })

        # 🔒 2. Cardápio (planejamento institucional)
        itens_cardapio = CardapioItem.objects.filter(receita=receita)

        if itens_cardapio.exists():
            for item in itens_cardapio.select_related("dia__semana__cardapio"):
                bloqueios.append({
                    "tipo": "Cardápio Escolar",
                    "descricao": f"{item.dia.semana.cardapio.nome} - {item.dia.get_dia_semana_display()}",
                    "url": reverse("merendaEscolar:cardapio_detail", args=[item.dia.semana.cardapio.id])
                })

        context["bloqueios"] = bloqueios
        context["possui_vinculo"] = len(bloqueios) > 0

        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            "Receita institucional excluída com sucesso."
        )
        return super().form_valid(form)