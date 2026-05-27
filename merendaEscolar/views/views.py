from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import (
    Avg,
    Count,
    Exists,
    OuterRef,
    Q,
    Sum,
)
from django.db.models.functions import Round, TruncMonth
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

from core.groups.nutricionista import NutricionistaRequiredMixin
from core.models import ConfiguraPessoal
from core.views.baseNutricionista import BaseNutricionistaView

from merendaEscolar.models import (
    CategoriaProduto,
    DivergenciaEntrega,
    Escola,
    EstoqueCentral,
    EstoqueEscola,
    MovimentacaoEstoque,
    Produto,
    ReceitaIngrediente,
    Transferencia,
    TransferenciaItem,
    UnidadeMedida,
)


class SuccessMessageMixin:
    success_message = ""

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return response


class ErrorMessageMixin:
    error_message = "Ocorreu um erro ao processar a solicitação."

    def form_invalid(self, form):
        messages.error(self.request, self.error_message)
        return super().form_invalid(form)



class UnidadeMedidaListView(BaseNutricionistaView, ListView):
    model = UnidadeMedida
    template_name = "merendaEscolar/unidade_medida/list.html"
    context_object_name = "unidades"
    paginate_by = 10

    def get_queryset(self):
        """
        Sobrescrevemos o queryset padrão para adicionar uma informação
        auxiliar em cada objeto retornado.

        Para cada unidade de medida, verificamos se existe algum registro
        relacionado (por exemplo, produtos que utilizam essa unidade).

        Se existir vínculo:
            unidade.tem_vinculo = True

        Se não existir:
            unidade.tem_vinculo = False

        O template usa essa informação para decidir se deve ou não
        exibir o botão de exclusão para o usuário.
        """

        queryset = super().get_queryset()

        for unidade in queryset:

            # Verifica se existe algum produto vinculado a esta unidade.
            # O related_name "produtos" deve existir no model Produto.
            unidade.tem_vinculo = unidade.produtos.exists()

        return queryset



class UnidadeMedidaCreateView(BaseNutricionistaView, SuccessMessageMixin,
    ErrorMessageMixin,
    CreateView

):
    model = UnidadeMedida
    fields = ["nome", "sigla"]
    template_name = "merendaEscolar/unidade_medida/form.html"
    success_url = reverse_lazy("merendaEscolar:unidade_medida_list")
    success_message = "Unidade de medida cadastrada com sucesso."
    error_message = "Erro ao cadastrar a unidade de medida."


class UnidadeMedidaUpdateView(BaseNutricionistaView,
    SuccessMessageMixin,
    ErrorMessageMixin,
    UpdateView
):
    model = UnidadeMedida
    fields = ["nome", "sigla"]
    template_name = "merendaEscolar/unidade_medida/form.html"
    success_url = reverse_lazy("merendaEscolar:unidade_medida_list")
    success_message = "Unidade de medida atualizada com sucesso."
    error_message = "Erro ao atualizar a unidade de medida."




class UnidadeMedidaDeleteView(BaseNutricionistaView, DeleteView):

    model = UnidadeMedida
    template_name = "merendaEscolar/unidade_medida/confirm_delete.html"
    success_url = reverse_lazy("merendaEscolar:unidade_medida_list")

    def delete(self, request, *args, **kwargs):
        """
        Executa a exclusão da unidade de medida com validação
        de integridade referencial.
        """

        self.object = self.get_object()

        try:
            # Verifica se existe produto utilizando esta unidade
            if self.object.produtos.exists():

                messages.warning(
                    request,
                    "Esta unidade de medida não pode ser excluída pois já está vinculada a produtos cadastrados."
                )

                return redirect(self.success_url)

            nome_unidade = str(self.object)

            self.object.delete()

            messages.success(
                request,
                f'A unidade de medida "{nome_unidade}" foi excluída com sucesso.'
            )

            return redirect(self.success_url)

        except Exception:
            # Tratamento defensivo para falhas inesperadas

            messages.error(
                request,
                "Ocorreu um erro inesperado ao tentar excluir a unidade de medida."
            )

            return redirect(self.success_url)


class CategoriaProdutoListView(BaseNutricionistaView, ListView):
    """
    Listagem institucional de categorias de produto.

    Estratégia:
    - O banco calcula o total de produtos vinculados
    - A view deriva propriedades de controle (tem_vinculo, pode_excluir)
    - O template apenas consome essas propriedades
    """

    model = CategoriaProduto
    template_name = "merendaEscolar/categoria_produto/list.html"
    context_object_name = "categorias"
    paginate_by = 10

    def get_queryset(self):
        queryset = (
            CategoriaProduto.objects
            .annotate(total_produtos=Count("produtos"))
            .order_by("nome")
        )

        for categoria in queryset:

            # indicador de vínculo
            categoria.tem_vinculo = categoria.total_produtos > 0

            # regra institucional de exclusão
            categoria.pode_excluir = categoria.total_produtos == 0

            # indicador visual para o template
            categoria.status_visual = (
                "Em uso" if categoria.tem_vinculo else "Disponível"
            )

        return queryset


class CategoriaProdutoCreateView(BaseNutricionistaView,
    SuccessMessageMixin,
    ErrorMessageMixin,
    CreateView
):
    model = CategoriaProduto
    fields = ["nome", "descricao"]
    template_name = "merendaEscolar/categoria_produto/form.html"
    success_url = reverse_lazy("merendaEscolar:categoria_produto_list")
    success_message = "Categoria cadastrada com sucesso."
    error_message = "Erro ao cadastrar a categoria."


class CategoriaProdutoUpdateView(BaseNutricionistaView,
    SuccessMessageMixin,
    ErrorMessageMixin,
    UpdateView
):
    model = CategoriaProduto
    fields = ["nome", "descricao"]
    template_name = "merendaEscolar/categoria_produto/form.html"
    success_url = reverse_lazy("merendaEscolar:categoria_produto_list")
    success_message = "Categoria atualizada com sucesso."
    error_message = "Erro ao atualizar a categoria."



class CategoriaProdutoDeleteView(BaseNutricionistaView, DeleteView):
    """
    Exclusão de Categoria de Produto.

    Regras institucionais:

    - Uma categoria NÃO pode ser excluída se possuir produtos vinculados.
    - A validação ocorre no backend para garantir integridade do sistema.
    - Sempre enviamos feedback ao usuário utilizando Django Messages.
    """

    model = CategoriaProduto
    template_name = "merendaEscolar/categoria_produto/confirm_delete.html"
    success_url = reverse_lazy("merendaEscolar:categoria_produto_list")

    def delete(self, request, *args, **kwargs):

        self.object = self.get_object()

        # Verifica se existem produtos vinculados à categoria
        if self.object.produtos.exists():

            messages.warning(
                request,
                "Esta categoria não pode ser excluída pois possui produtos vinculados."
            )

            return redirect(self.success_url)

        nome_categoria = self.object.nome

        # exclusão segura
        self.object.delete()

        messages.success(
            request,
            f'A categoria "{nome_categoria}" foi excluída com sucesso.'
        )

        return redirect(self.success_url)
    
# Produtos
class ProdutoListView(BaseNutricionistaView,
    ListView
):
    model = Produto
    template_name = "merendaEscolar/produto/list.html"
    context_object_name = "produtos"
    paginate_by = 10


    def get_queryset(self):
        queryset = (
            Produto.objects
            .select_related("categoria", "unidade_medida")
            .annotate(
                possui_estoque_central=Exists(
                    EstoqueCentral.objects.filter(produto=OuterRef("pk"))
                ),
                possui_estoque_escola=Exists(
                    EstoqueEscola.objects.filter(produto=OuterRef("pk"))
                ),
                possui_movimentacao=Exists(
                    MovimentacaoEstoque.objects.filter(produto=OuterRef("pk"))
                ),
                possui_receita=Exists(
                    ReceitaIngrediente.objects.filter(produto=OuterRef("pk"))
                ),
            )
            .order_by("nome")
        )

        search = self.request.GET.get("search", "").strip()

        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) |
                Q(codigo__icontains=search) |
                Q(categoria__nome__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        base_queryset = Produto.objects.all()

        context["total_produtos"] = base_queryset.count()
        context["total_ativos"] = base_queryset.filter(ativo=True).count()
        context["total_inativos"] = base_queryset.filter(ativo=False).count()

        return context


class ProdutoCreateView(BaseNutricionistaView,
    SuccessMessageMixin,
    ErrorMessageMixin,
    CreateView
):
    model = Produto
    fields = [
        "nome",
        "descricao",
        "categoria",
        "unidade_medida",
        "ativo"
    ]
    template_name = "merendaEscolar/produto/form.html"
    success_url = reverse_lazy("merendaEscolar:produto_list")
    success_message = "Produto cadastrado com sucesso."
    error_message = "Erro ao cadastrar o produto."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Produto"
        context["titulo"] = "Produto"
        return context


class ProdutoUpdateView(BaseNutricionistaView,
    SuccessMessageMixin,
    ErrorMessageMixin,
    UpdateView
):
    model = Produto
    fields = [
        "nome",
        "descricao",
        "categoria",
        "unidade_medida",
        "ativo"
    ]
    template_name = "merendaEscolar/produto/form.html"
    success_url = reverse_lazy("merendaEscolar:produto_list")
    success_message = "Produto atualizado com sucesso."
    error_message = "Erro ao atualizar o produto."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Produto"
        return context    


class ProdutoDeleteView(BaseNutricionistaView,
    DeleteView
):
    model = Produto
    template_name = "merendaEscolar/produto/delete.html"
    success_url = reverse_lazy("merendaEscolar:produto_list")

    def dispatch(self, request, *args, **kwargs):
        produto = self.get_object()

        if self._possui_vinculos(produto):
            messages.error(
                request,
                "Este produto possui vínculos institucionais e não pode ser excluído."
            )
            return redirect("merendaEscolar:produto_list")

        return super().dispatch(request, *args, **kwargs)

    def _possui_vinculos(self, produto):

        if produto.estoque_central.exists():
            return True

        if EstoqueEscola.objects.filter(produto=produto).exists():
            return True

        if MovimentacaoEstoque.objects.filter(produto=produto).exists():
            return True

        if ReceitaIngrediente.objects.filter(produto=produto).exists():
            return True

        if TransferenciaItem.objects.filter(produto=produto).exists():
            return True

        return False
    
    
# daqui pra baixo sao os exemplos de dashboards

def quantize2(valor):
    """Arredonda para 2 casas decimais."""
    if valor is None:
        return Decimal("0.00")
    return Decimal(str(valor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

class DashboardNutricionalView(BaseNutricionistaView, TemplateView):

    template_name = "merendaEscolar/dashboard_nutricionista.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        hoje = timezone.now()
        mes_inicio = hoje.replace(day=1)

        """
        IMPORTANTE:
        Usamos annotate() para realizar cálculos diretamente no banco.

        Isso evita loops Python e permite que o banco execute
        agregações com alta performance, essencial para redes
        municipais com muitas escolas.
        """

        # =========================
        # INDICADORES GERAIS
        # =========================

        context["total_produtos"] = Produto.objects.count()

        context["estoque_total_central"] = (
            EstoqueCentral.objects.aggregate(
                total=Sum("quantidade")
            )["total"] or 0
        )
        
        context["estoque_total_escolas"] = EstoqueEscola.objects.filter(quantidade__gt=0).aggregate(total=Round(Sum("quantidade")))["total"]

        context["movimentacoes_mes"] = (
            MovimentacaoEstoque.objects
            .filter(data_movimentacao__gte=mes_inicio)
            .count()
        )


        # =========================
        # ESTOQUE POR CATEGORIA
        # =========================

        estoque_categoria = (
            CategoriaProduto.objects
            .annotate(
                total=Round(Sum("produtos__estoque_central__quantidade"))
            )
            .values("nome", "total")
        )

        context["estoque_categoria"] = list(estoque_categoria)

        # =========================
        # ESTOQUE POR ESCOLA
        # =========================

        estoque_escolas = (
            EstoqueEscola.objects
            .values("escola__nome_escola")
            .annotate(total=Round(Sum("quantidade")))
            .order_by("-total")[:10]
        )

        context["estoque_escolas"] = list(estoque_escolas)

        # =========================
        # PRODUTOS MAIS CONSUMIDOS
        # =========================

        consumo_produtos = (
            MovimentacaoEstoque.objects
            .filter(tipo="SAIDA_ESCOLA")
            .values("produto__nome", "produto__unidade_medida__sigla")
            .annotate(total=Round(Sum("quantidade")))
            .order_by("-total")[:10]
        )       

        context["consumo_produtos"] = list(consumo_produtos)

        # =========================
        # MOVIMENTAÇÃO MENSAL
        # =========================

        historico = (
            MovimentacaoEstoque.objects
            .annotate(mes=TruncMonth("data_movimentacao"))
            .values("mes")
            .annotate(total=Count("id"))
            .order_by("mes")
        )

        context["historico"] = list(historico)

        # =========================
        # LOGÍSTICA
        # =========================

        context["transferencias_pendentes"] = Transferencia.objects.filter(
            status="ENVIADO"
        ).count()

        context["entregas_conferencia"] = Transferencia.objects.filter(
            status="EM_CONFERENCIA"
        ).count()

        context["divergencias_abertas"] = DivergenciaEntrega.objects.filter(
            status="ABERTA"
        ).count()

        messages.success(
            self.request,
            "Painel nutricional carregado com sucesso."
        )

        return context  
    

class EstoqueCentralListView(BaseNutricionistaView, ListView):
    """
    Dashboard institucional do estoque central da merenda escolar.

    A view fornece:

    - visão consolidada do estoque
    - monitoramento de validade de produtos
    - indicadores logísticos da distribuição
    - métricas operacionais da rede escolar

    IMPORTANTE
    Itens com quantidade zero são ocultados da listagem,
    pois já foram consumidos ou descartados.
    O histórico permanece no banco para auditoria.
    """

    model = EstoqueCentral
    template_name = "merendaEscolar/estoque/estoque.html"
    context_object_name = "produtos"
    
    # Faz com o que os dados de configuração sejam carregados antes de todo o conteudo da view
    def dispatch(self, request, *args, **kwargs):
        self.configuracao, _ = ConfiguraPessoal.objects.get_or_create(pk=1)
        return super().dispatch(request, *args, **kwargs)

    # Define a quantidade de registros na tela
    def get_paginate_by(self, queryset):
        return self.configuracao.pagina_estoqueCentral

    # ====================================
    # QUERYSET PRINCIPAL (ESTOQUE ATIVO)
    # ====================================

    def get_queryset(self):
        """
        Query otimizada evitando N+1 queries e
        ocultando itens sem saldo disponível.
        """

        queryset = (
            EstoqueCentral.objects
            .select_related("produto")
            .filter(quantidade__gt=0)  # Oculta itens descartados ou zerados
            .order_by("produto__nome")
        )

        status = self.request.GET.get("status")

        hoje = timezone.now().date()
        critico = hoje + timedelta(days=7)
        alerta = hoje + timedelta(days=30)

        if status == "vencido":
            queryset = queryset.filter(data_validade__lt=hoje)

        elif status == "critico":
            queryset = queryset.filter(
                data_validade__gte=hoje,
                data_validade__lte=critico
            )

        elif status == "alerta":
            queryset = queryset.filter(
                data_validade__gt=critico,
                data_validade__lte=alerta
            )

        return queryset

    # ====================================
    # CONTEXTO DO DASHBOARD
    # ====================================

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        hoje = timezone.now().date()
        agora = timezone.now()

        critico = hoje + timedelta(days=7)
        alerta = hoje + timedelta(days=30)

        """
        IMPORTANTE

        Todas as métricas usam aggregate() ou filtros no banco
        para evitar loops Python e garantir escalabilidade.
        """

        estoque_ativo = EstoqueCentral.objects.filter(quantidade__gt=0)

        # =========================
        # KPIs OPERACIONAIS
        # =========================

        context["total_itens_estoque"] = estoque_ativo.count()

        context["quantidade_total_estoque"] = (
            estoque_ativo.aggregate(total=Sum("quantidade"))["total"] or 0
        )

        context["escolas_atendidas"] = Escola.objects.count()

        context["pagina_transferencia"] = self.configuracao.pagina_estoqueCentral
        # 🔷 Fonte única de verdade (governança)
        context["page_size_options"] = [5,10, 20, 30, 50]   

        # =========================
        # INDICADORES LOGÍSTICOS
        # =========================

        context["envios_mes"] = Transferencia.objects.filter(
            status__in=["ENVIADO", "EM_CONFERENCIA", "RECEBIDO"],
            enviado_em__month=agora.month,
            enviado_em__year=agora.year
        ).count()

        context["transferencias_pendentes"] = Transferencia.objects.filter(
            status="ENVIADO"
        ).count()

        context["entregas_em_conferencia"] = Transferencia.objects.filter(
            status="EM_CONFERENCIA"
        ).count()

        context["divergencias_abertas"] = (
            DivergenciaEntrega.objects
            .filter(status__in=["ABERTA", "EM_ANALISE"])
            .count()
        )

        # =========================
        # MONITORAMENTO DE VALIDADE
        # =========================

        context["lotes_vencidos"] = estoque_ativo.filter(
            data_validade__lt=hoje
        ).count()

        context["lotes_criticos"] = estoque_ativo.filter(
            data_validade__gte=hoje,
            data_validade__lte=critico
        ).count()

        context["lotes_alerta"] = estoque_ativo.filter(
            data_validade__gt=critico,
            data_validade__lte=alerta
        ).count()

        # =========================
        # ALERTAS OPERACIONAIS
        # =========================

        if context["lotes_vencidos"] > 0:

            messages.warning(
                self.request,
                f"Atenção: existem {context['lotes_vencidos']} lotes vencidos no estoque central."
            )

        elif context["lotes_criticos"] > 0:

            messages.info(
                self.request,
                f"{context['lotes_criticos']} lotes estão próximos do vencimento."
            )

        if not context["produtos"]:

            messages.info(
                self.request,
                "Nenhum produto disponível no estoque central com os filtros aplicados."
            )

        # =========================
        # FEEDBACK FINAL
        # =========================

        messages.success(
            self.request,
            "Painel do estoque central carregado com sucesso."
        )

        return context