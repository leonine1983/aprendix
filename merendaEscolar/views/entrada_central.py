from django.views.generic import FormView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q

from ..models import (
    EstoqueCentral,
    MovimentacaoEstoque,
    Escola,
    DivergenciaEntrega
)
from ..forms import EntradaEstoqueCentralForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

from core.permissions import GroupRequiredMixin
from core.groups.nutricionista import NUTRICIONISTA_GROUPS
from django.core.exceptions import PermissionDenied



class ErrorMessageMixin:
    error_message = "Ocorreu um erro ao processar a solicitação."

    def form_invalid(self, form):
        messages.error(self.request, self.error_message)
        return super().form_invalid(form)


# ===============================
# ENTRADA DE ESTOQUE CENTRAL
# ===============================

class EntradaEstoqueCentralView(
    LoginRequiredMixin,
    GroupRequiredMixin,
    PermissionRequiredMixin,
    SuccessMessageMixin,
    ErrorMessageMixin,
    FormView,
):
    permission_required = "merendaEscolar.add_estoquecentral"
    group_required = NUTRICIONISTA_GROUPS

    template_name = "merendaEscolar/estoque/entrada_central_form.html"
    form_class = EntradaEstoqueCentralForm
    success_url = reverse_lazy("merendaEscolar:entrada-central")  # corrigido namespace

    def form_valid(self, form):
        produto = form.cleaned_data["produto"]
        lote = form.cleaned_data["lote"]
        data_validade = form.cleaned_data["data_validade"]
        quantidade = form.cleaned_data["quantidade"]
        observacao = form.cleaned_data["observacao"]

        with transaction.atomic():

            estoque, created = EstoqueCentral.objects.select_for_update().get_or_create(
                produto=produto,
                lote=lote,
                defaults={
                    "quantidade": 0,
                    "data_validade": data_validade
                }
            )

            estoque.quantidade += quantidade

            if data_validade:
                estoque.data_validade = data_validade

            estoque.save()

            # corrigido: tipo como string (seu model não usa enum)
            MovimentacaoEstoque.objects.create(
                produto=produto,
                quantidade=quantidade,
                tipo="ENTRADA_CENTRAL",
                usuario=self.request.user,
                observacao=observacao
            )

        messages.success(self.request, "Entrada registrada com sucesso no estoque central.")
        return super().form_valid(form)   


# ===============================
# DASHBOARD ESTOQUE CENTRAL
# ===============================
class EstoqueCentralListView(LoginRequiredMixin,
                            GroupRequiredMixin,
                            PermissionRequiredMixin,
                              ListView):
    model = EstoqueCentral
    permission_required = permission_required = "merendaEscolar.view_estoquecentral"
    group_required = NUTRICIONISTA_GROUPS
    template_name = "merendaEscolar/estoque/estoque.html"
    context_object_name = "produtos"  
    
    def get_queryset(self):
        qs = (
            EstoqueCentral.objects
            .select_related("produto")
            .ordenado_por_validade()
        )

        filtro = self.request.GET.get("status")

        hoje = timezone.now().date()

        if filtro == "vencido":
            qs = qs.filter(data_validade__lt=hoje)

        elif filtro == "critico":
            qs = qs.filter(
                data_validade__gte=hoje,
                data_validade__lte=hoje + timedelta(days=7)
            )

        elif filtro == "alerta":
            qs = qs.filter(
                data_validade__gt=hoje + timedelta(days=7),
                data_validade__lte=hoje + timedelta(days=30)
            )

        return qs    
    
    def dispatch(self, request, *args, **kwargs):
        print("AUTH:", request.user.is_authenticated)
        print("USER:", request.user)
        print("SESSION:", request.session.session_key)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hoje = timezone.now().date()
        produtos_qs = context["produtos"]

        # ==========================================
        # DASHBOARD – INDICADORES GERAIS
        # ==========================================

        # Total consolidado em estoque
        total_itens_estoque = produtos_qs.aggregate(
            total=Sum("quantidade")
        )["total"] or 0

        # Escolas cadastradas
        escolas_atendidas = Escola.objects.count()

        # Primeiro dia do mês
        inicio_mes = hoje.replace(day=1)

        # Movimentações de saída no mês
        envios_mes = MovimentacaoEstoque.objects.filter(
            tipo="SAIDA_CENTRAL",
            data_movimentacao__date__gte=inicio_mes
        ).count()

        # Divergências abertas
        divergencias_abertas = DivergenciaEntrega.objects.filter(
            status="ABERTA"
        ).count()

        # ==========================================
        # KPIs DE VALIDADE
        # ==========================================

        lotes_vencidos = produtos_qs.filter(
            data_validade__lt=hoje
        ).count()

        lotes_criticos = produtos_qs.filter(
            data_validade__gte=hoje,
            data_validade__lte=hoje + timedelta(days=7)
        ).count()

        lotes_alerta = produtos_qs.filter(
            data_validade__gt=hoje + timedelta(days=7),
            data_validade__lte=hoje + timedelta(days=30)
        ).count()

        lotes_normais = produtos_qs.filter(
            data_validade__gt=hoje + timedelta(days=30)
        ).count()

        # ==========================================
        # Atualiza Contexto
        # ==========================================

        context.update({
            "total_itens_estoque": total_itens_estoque,
            "escolas_atendidas": escolas_atendidas,
            "envios_mes": envios_mes,
            "divergencias_abertas": divergencias_abertas,

            "lotes_vencidos": lotes_vencidos,
            "lotes_criticos": lotes_criticos,
            "lotes_alerta": lotes_alerta,
            "lotes_normais": lotes_normais,
        })
        

        return context
