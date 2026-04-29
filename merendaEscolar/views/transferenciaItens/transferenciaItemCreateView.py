from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django import forms
from django.db import transaction
from django.core.exceptions import ValidationError
from ...models import Transferencia, TransferenciaItem, EstoqueCentral
from core.permissions import GroupRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from core.groups.nutricionista import NUTRICIONISTA_GROUPS
from django.core.exceptions import PermissionDenied


class TransferenciaItemForm(forms.ModelForm):
    """
    Formulário para inclusão de item em transferência.
    O lote (estoque_origem) é definido automaticamente pela View com estratégia FEFO,
    mas ainda precisa existir no form para manipulação.
    """

    estoque_origem = forms.ModelChoiceField(
        queryset=EstoqueCentral.objects.none(),
        required=False,
        label="Lote de Origem",
    )

    class Meta:
        model = TransferenciaItem
        fields = ["produto", "quantidade", "estoque_origem"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        produto_id = None

        # 1️⃣ POST
        if "produto" in self.data:
            try:
                produto_id = int(self.data.get("produto"))
            except (ValueError, TypeError):
                produto_id = None

        # 2️⃣ Edição
        elif self.instance.pk and self.instance.produto_id:
            produto_id = self.instance.produto_id

        if produto_id:
            qs = (
                EstoqueCentral.objects
                .filter(produto_id=produto_id, quantidade__gt=0)
                .order_by("data_validade")
            )
            self.fields["estoque_origem"].queryset = qs

            # Garantir que o lote enviado esteja no queryset
            if "estoque_origem" in self.data:
                lote_id = self.data.get("estoque_origem")
                if lote_id:
                    self.fields["estoque_origem"].queryset = EstoqueCentral.objects.filter(
                        pk=lote_id
                    ) | qs

            # Seleciona primeiro lote disponível
            if not self.instance.pk and qs.exists():
                self.initial["estoque_origem"] = qs.first()



from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django import forms
from django.db import transaction
from django.contrib import messages
from ...models import Transferencia, TransferenciaItem, EstoqueCentral

from core.permissions import GroupRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from core.groups.nutricionista import NUTRICIONISTA_GROUPS


class TransferenciaItemCreateView(
    LoginRequiredMixin,
    GroupRequiredMixin,
    PermissionRequiredMixin,
    CreateView
):
    model = TransferenciaItem
    form_class = TransferenciaItemForm
    template_name = "merendaEscolar/transferencia/transferenciaitem_form.html"

    permission_required = "merendaEscolar.add_transferenciaitem"
    group_required = NUTRICIONISTA_GROUPS

    def dispatch(self, request, *args, **kwargs):
        self.transferencia = get_object_or_404(
            Transferencia,
            pk=self.kwargs["pk"]
        )

        # 🔒 Regra institucional: só permite editar RASCUNHO
        if self.transferencia.status != "RASCUNHO":
            messages.error(
                request,
                "Não é possível adicionar itens a uma transferência já finalizada."
            )
            return redirect(
                "merendaEscolar:transferencia-detail",
                pk=self.transferencia.pk
            )

        return super().dispatch(request, *args, **kwargs)

    @transaction.atomic
    def form_valid(self, form):
        produto = form.cleaned_data["produto"]
        quantidade = form.cleaned_data["quantidade"]

        lote = (
            EstoqueCentral.objects
            .select_for_update()
            .filter(produto=produto, quantidade__gt=0)
            .order_by("data_validade")
            .first()
        )

        if not lote:
            form.add_error(
                "produto",
                "Não há saldo disponível no estoque central para este produto."
            )
            return self.form_invalid(form)

        if quantidade > lote.quantidade:
            form.add_error(
                "quantidade",
                f"Saldo disponível no lote: {lote.quantidade}."
            )
            return self.form_invalid(form)

        # 🔒 Regra de unicidade
        item_existente = TransferenciaItem.objects.filter(
            transferencia=self.transferencia,
            estoque_origem=lote
        ).first()

        if item_existente:
            messages.error(
                self.request,
                "Este lote já foi incluído nesta transferência. "
                "Edite o item existente para alterar a quantidade."
            )
            return self.form_invalid(form)

        # ✅ Persistência
        form.instance.transferencia = self.transferencia
        form.instance.estoque_origem = lote

        messages.success(
            self.request,
            "Item adicionado à transferência com sucesso."
        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "merendaEscolar:transferencia-detail",
            kwargs={"pk": self.transferencia.pk}
        )
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Produto selecionado via GET/POST
        produto_id = self.request.POST.get("produto") or self.request.GET.get("produto")

        lote_fefo = None
        saldo_disponivel = None
        total_lotes = 0

        if produto_id:
            lotes = (
                EstoqueCentral.objects
                .filter(produto_id=produto_id, quantidade__gt=0)
                .order_by("data_validade")
            )
            total_lotes = lotes.count()
            lote_fefo = lotes.first()

            if lote_fefo:
                saldo_disponivel = lote_fefo.quantidade

        ctx["lote_fefo"] = lote_fefo
        ctx["saldo_disponivel"] = saldo_disponivel
        ctx["total_lotes"] = total_lotes
        return ctx
        
    