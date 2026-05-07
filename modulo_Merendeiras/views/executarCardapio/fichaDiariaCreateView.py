from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages

from ...models import FichaExecucaoReceita, ExecucaoCardapioDia
from ..baseMerendeiraView import BaseMerendeiraView

from django import forms

from django.core.paginator import Paginator
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages
from django import forms

from ...models import FichaExecucaoReceita, ExecucaoCardapioDia
from ..baseMerendeiraView import BaseMerendeiraView


class FichaDiariaForm(forms.ModelForm):

    class Meta:
        model = FichaExecucaoReceita
        fields = [
            "porcoes_produzidas",
            "aceitabilidade",
            "houve_sobras",
            "motivo_sobras",
            "falta_alimento",
            "problema_equipamento",
            "falta_gas",
            "outra_ocorrencia",
            "observacoes",
        ]

        widgets = {
            "aceitabilidade": forms.Select(attrs={
                "class": "form-select"
            }),
            "houve_sobras": forms.Select(attrs={
                "class": "form-select"
            }),
            "motivo_sobras": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Motivo das sobras (se houver)"
            }),
            "outra_ocorrencia": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Descreva outra ocorrência"
            }),
            "observacoes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),
        }
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages

from ...models import FichaExecucaoReceita, ExecucaoCardapioDia
from ..baseMerendeiraView import BaseMerendeiraView


class FichaDiariaCreateView(BaseMerendeiraView, CreateView):
    model = FichaExecucaoReceita
    form_class = FichaDiariaForm
    template_name = "modulo_merendeiras/cadapioHoje/ficha_diaria.html"

    def dispatch(self, request, *args, **kwargs):
        self.turno = self.kwargs.get("turno")

        self.execucao = ExecucaoCardapioDia.objects.get(
            pk=self.kwargs["execucao_id"],
            turno=self.turno
        )

        # 🔥 AGORA O FILTRO É POR execucao_cardapio_dia
        self.ficha_existente = FichaExecucaoReceita.objects.filter(
            execucao_cardapio_dia=self.execucao
        ).first()

        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["execucao"] = self.execucao
        ctx["modo_edicao"] = bool(self.ficha_existente)
        ctx["usuario_nome"] = self.request.user.get_full_name() or self.request.user.username

        # ── DEBUG — remova depois de confirmar ──
        itens_exec_qs = self.execucao.itens_executados.select_related(
            "execucao_receita", "receita"
        ).prefetch_related("execucao_receita__movimentacoes__produto")

        print(f"\n[DEBUG] execucao.id={self.execucao.id} cardapio_dia={self.execucao.cardapio_dia_id}")
        print(f"[DEBUG] total itens_executados: {itens_exec_qs.count()}")

        for ie in itens_exec_qs:
            print(f"  item: {ie.receita.nome} | execucao_receita: {ie.execucao_receita_id}")
            if ie.execucao_receita:
                movs = ie.execucao_receita.movimentacoes.all()
                print(f"    movimentacoes: {movs.count()}")
                for m in movs:
                    print(f"      tipo={m.tipo} produto={m.produto} qtd={m.quantidade}")

        # ── Monta itens_alimentos ──
        itens = []

        if self.ficha_existente:
            saved_itens = self.ficha_existente.itens.select_related("produto", "unidade")
            if saved_itens.exists():
                itens = list(saved_itens)

        if not itens:
            from collections import defaultdict
            agregado = defaultdict(lambda: {"quantidade": 0, "unidade": "", "produto_nome": ""})

            for ie in itens_exec_qs:
                if not ie.execucao_receita:
                    continue
                for mov in ie.execucao_receita.movimentacoes.all():
                    if mov.tipo != "RETIRADA_RECEITA" or not mov.produto:
                        continue
                    key = mov.produto.id
                    agregado[key]["produto_nome"] = mov.produto.nome
                    # unidade_medida pode ser FK ou CharField — adapta aqui
                    unidade = getattr(mov.produto, "unidade_medida", None)
                    if unidade and hasattr(unidade, "simbolo"):
                        agregado[key]["unidade"] = unidade.simbolo
                    elif unidade:
                        agregado[key]["unidade"] = str(unidade)
                    agregado[key]["quantidade"] += float(mov.quantidade)

            itens = list(agregado.values())
            print(f"[DEBUG] itens_alimentos montados: {itens}")

        ctx["itens_alimentos"] = itens

        # ── Receitas executadas para exibir no cabeçalho ──
        # Independente do cardapio_dia, monta a lista a partir dos itens_executados
        ctx["receitas_executadas"] = [
            {
                "nome": ie.receita.nome,
                "status": ie.get_status_display(),
                "porcoes": ie.porcoes_executadas,
                "motivo_falha": ie.motivo_falha,
            }
            for ie in itens_exec_qs
        ]

        return ctx


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if self.ficha_existente:
            # modo edição: carrega instância existente
            kwargs["instance"] = self.ficha_existente
        else:
            # modo criação: pré-popula porcoes_produzidas com quantidade_alunos da execução
            if self.request.method == "GET":
                kwargs["initial"] = {
                    "porcoes_produzidas": self.execucao.quantidade_alunos,
                }

        return kwargs

    
    def form_valid(self, form):
        try:
            with transaction.atomic():

                ficha = form.save(commit=False)

                # 🔥 CAMPOS CORRETOS DO NOVO MODEL
                ficha.execucao_cardapio_dia = self.execucao
                ficha.usuario = self.request.user

                ficha.save()

                if self.ficha_existente:
                    messages.success(self.request, "Ficha atualizada com sucesso.")
                else:
                    messages.success(self.request, "Ficha registrada com sucesso.")

        except Exception as e:
            messages.error(self.request, f"Erro ao salvar ficha: {str(e)}")
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        return self.request.path