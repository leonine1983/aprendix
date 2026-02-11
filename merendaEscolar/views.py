from django.shortcuts import render
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from rh.models import Escola

from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy

from .models import EstoqueCentral, UnidadeMedida, CategoriaProduto, Produto
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q



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



# Unidade de Medida
class UnidadeMedidaListView(LoginRequiredMixin, ListView):
    model = UnidadeMedida
    template_name = "unidade_medida/list.html"
    context_object_name = "unidades"
    paginate_by = 10



class UnidadeMedidaCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SuccessMessageMixin,
    ErrorMessageMixin,
    CreateView
):
    model = UnidadeMedida
    fields = ["nome", "sigla"]
    template_name = "unidade_medida/form.html"
    success_url = reverse_lazy("merendaEscolar:unidade_medida_list")
    permission_required = "estoque.add_unidademedida"
    success_message = "Unidade de medida cadastrada com sucesso."
    error_message = "Erro ao cadastrar a unidade de medida."


class UnidadeMedidaUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SuccessMessageMixin,
    ErrorMessageMixin,
    UpdateView
):
    model = UnidadeMedida
    fields = ["nome", "sigla"]
    template_name = "unidade_medida/form.html"
    success_url = reverse_lazy("merendaEscolar:unidade_medida_list")
    permission_required = "estoque.change_unidademedida"
    success_message = "Unidade de medida atualizada com sucesso."
    error_message = "Erro ao atualizar a unidade de medida."



# Categoria de Produto
class CategoriaProdutoListView(LoginRequiredMixin, ListView):
    model = CategoriaProduto
    template_name = "categoria_produto/list.html"
    context_object_name = "categorias"
    paginate_by = 10


class CategoriaProdutoCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SuccessMessageMixin,
    ErrorMessageMixin,
    CreateView
):
    model = CategoriaProduto
    fields = ["nome", "descricao"]
    template_name = "categoria_produto/form.html"
    success_url = reverse_lazy("merendaEscolar:categoria_produto_list")
    permission_required = "estoque.add_categoriaproduto"
    success_message = "Categoria cadastrada com sucesso."
    error_message = "Erro ao cadastrar a categoria."


class CategoriaProdutoUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SuccessMessageMixin,
    ErrorMessageMixin,
    UpdateView
):
    model = CategoriaProduto
    fields = ["nome", "descricao"]
    template_name = "categoria_produto/form.html"
    success_url = reverse_lazy("merendaEscolar:categoria_produto_list")
    permission_required = "estoque.change_categoriaproduto"
    success_message = "Categoria atualizada com sucesso."
    error_message = "Erro ao atualizar a categoria."

# Produtos
from django.db.models import Q

class ProdutoListView(LoginRequiredMixin, ListView):
    model = Produto
    template_name = "produto/list.html"
    context_object_name = "produtos"
    paginate_by = 10

    def get_queryset(self):
        queryset = (
            Produto.objects
            .select_related("categoria", "unidade_medida")
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



class ProdutoCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
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
    template_name = "produto/form.html"
    success_url = reverse_lazy("merendaEscolar:produto_list")
    permission_required = "estoque.add_produto"
    success_message = "Produto cadastrado com sucesso."
    error_message = "Erro ao cadastrar o produto."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Produto"
        return context


class ProdutoUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
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
    template_name = "produto/form.html"
    success_url = reverse_lazy("merendaEscolar:produto_list")
    permission_required = "estoque.change_produto"
    success_message = "Produto atualizado com sucesso."
    error_message = "Erro ao atualizar o produto."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Produto"
        return context







def inicio_merenda(request):
    hoje = timezone.now().date()
    limite_alerta_validade = hoje + timedelta(days=30)

    # =========================
    # BASE DO ESTOQUE
    # =========================
    """estoques = (
        EstoqueCentral.objects
        .select_related(
            "produto",
            "produto__unidade_medida",
            "unidade_escolar"
        )
        .filter(quantidade__gt=0)
    )

    # =========================
    # CARDS
    # =========================

    # Total de itens em estoque (registros)
    total_itens_estoque = estoques.count()

    # Escolas atendidas
    escolas_atendidas = (
        estoques
        .values("unidade_escolar")
        .distinct()
        .count()
    )

    # Envios no mês (placeholder inteligente)
    # Ideal: usar um model de MovimentacaoEstoque
    envios_mes = 0

    # Alertas ativos
    alertas_ativos = estoques.filter(
        quantidade__lte=10
    ).count() + estoques.filter(
        data_validade__lte=limite_alerta_validade
    ).count()

    # =========================
    # TABELA DE PRODUTOS
    # =========================
    produtos_tabela = []

    for item in estoques:
        # Regra de status
        if item.data_validade and item.data_validade < hoje:
            status = "Vencido"
            status_css = "alerta"
        elif item.quantidade <= 10:
            status = "Baixo"
            status_css = "alerta"
        else:
            status = "Adequado"
            status_css = "ok"

        produtos_tabela.append({
            "nome": item.produto.nome,
            "quantidade": f"{item.quantidade} {item.produto.unidade_medida.sigla}",
            "validade": item.data_validade.strftime("%m/%Y") if item.data_validade else "-",
            "status": status,
            "status_css": status_css,
        })"""

    # =========================
    # CONTEXTO FINAL
    # =========================
    context = {
        "total_itens_estoque": "total_itens_estoque",
        "escolas_atendidas": "escolas_atendidas",
        "envios_mes": "envios_mes",
        "alertas_ativos": "alertas_ativos",
        "produtos": "produtos_tabela",
    }

    return render(request, "dashboard.html", context)
