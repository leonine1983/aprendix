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
    PermissionDenied,
    SuccessMessageMixin,
    ErrorMessageMixin,
    FormView,
):
    group_required = NUTRICIONISTA_GROUPS
    raise_exception = True  
    

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

