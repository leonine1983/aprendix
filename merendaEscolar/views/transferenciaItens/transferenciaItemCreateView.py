from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
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


class TransferenciaItemCreateView(CreateView):
    model = TransferenciaItem
    form_class = TransferenciaItemForm
    template_name = "merendaEscolar/transferencia/transferencia_item_form.html"
    LoginRequiredMixin,
    GroupRequiredMixin,
    PermissionRequiredMixin,

    permission_required = "estoque.add_unidademedida"
    group_required = NUTRICIONISTA_GROUPS

    def dispatch(self, request, *args, **kwargs):
        self.transferencia = get_object_or_404(
            Transferencia, pk=self.kwargs["pk"]
        )
        return super().dispatch(request, *args, **kwargs)

    @transaction.atomic
    def form_valid(self, form):
        produto = form.cleaned_data["produto"]
        quantidade = form.cleaned_data["quantidade"]

        # Buscar lote automaticamente (FEFO)
        lote = (
            EstoqueCentral.objects
            .select_for_update()  # 🔒 trava concorrência
            .filter(produto=produto, quantidade__gt=0)
            .order_by("data_validade")
            .first()
        )

        if not lote:
            form.add_error(
                "produto", "Não há saldo disponível no estoque central para este produto."
            )
            return self.form_invalid(form)

        if quantidade > lote.quantidade:
            form.add_error(
                "quantidade", f"Saldo disponível no lote: {lote.quantidade}."
            )
            return self.form_invalid(form)

        form.instance.transferencia = self.transferencia
        form.instance.estoque_origem = lote

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "merendaEscolar:transferencia-detail", kwargs={"pk": self.transferencia.pk}
        )