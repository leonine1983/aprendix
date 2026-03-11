from django.shortcuts import render, redirect
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from rh.models import Escola

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from ..models import EstoqueCentral, UnidadeMedida, CategoriaProduto, Produto
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from core.permissions import GroupRequiredMixin
from core.groups.nutricionista import NUTRICIONISTA_GROUPS
from django.core.exceptions import PermissionDenied



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



class UnidadeMedidaListView(
    LoginRequiredMixin,
    ListView
):
    """
    Lista paginada das unidades de medida cadastradas no sistema.

    Esta view possui também uma responsabilidade adicional:
    informar ao template se cada unidade de medida possui vínculo
    com outros registros do sistema (ex: produtos cadastrados).

    Essa informação é utilizada para fins de segurança na interface,
    permitindo exibir o botão "Excluir" apenas quando a unidade ainda
    não estiver sendo utilizada por nenhuma outra tabela.

    IMPORTANTE:
    Mesmo com essa verificação no template, a validação definitiva
    deve ocorrer também na view de exclusão para garantir integridade
    de dados no backend.
    """

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



class UnidadeMedidaCreateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    ErrorMessageMixin,
    CreateView

):
    model = UnidadeMedida
    fields = ["nome", "sigla"]
    template_name = "merendaEscolar/unidade_medida/form.html"
    success_url = reverse_lazy("merendaEscolar:unidade_medida_list")
    success_message = "Unidade de medida cadastrada com sucesso."
    error_message = "Erro ao cadastrar a unidade de medida."


class UnidadeMedidaUpdateView(
    LoginRequiredMixin,
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




class UnidadeMedidaDeleteView(LoginRequiredMixin, DeleteView):
    """
    Exclusão institucional de Unidade de Medida.

    Regras de negócio aplicadas:

    1) Uma unidade de medida NÃO pode ser excluída caso exista
       qualquer Produto vinculado a ela.

    2) A validação ocorre obrigatoriamente no backend para garantir
       integridade referencial do banco de dados.

    3) O template apenas solicita confirmação da ação do usuário.

    4) Todas as respostas da view enviam mensagens ao usuário,
       seguindo a diretriz institucional de feedback explícito
       utilizando o Django Messages Framework.
    """

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


# Categoria de Produto
class CategoriaProdutoListView(
    LoginRequiredMixin,
    ListView
):
    model = CategoriaProduto
    template_name = "merendaEscolar/categoria_produto/list.html"
    context_object_name = "categorias"
    paginate_by = 10




class CategoriaProdutoCreateView(
    LoginRequiredMixin,
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


class CategoriaProdutoUpdateView(
    LoginRequiredMixin,
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

# Produtos
from django.db.models import Q

class ProdutoListView(
    LoginRequiredMixin,
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


class ProdutoUpdateView(
    LoginRequiredMixin,
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
    success_message = "Produto atualizado com sucesso."
    error_message = "Erro ao atualizar o produto."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Produto"
        return context


@login_required
def inicio_merenda(request):

    if not request.user.is_superuser and not request.user.groups.filter(name__in=NUTRICIONISTA_GROUPS).exists():
        raise PermissionDenied("Acesso restrito ao módulo Merenda Escolar.")

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

    return render(request, "merendaEscolar/dashboard.html", context)
