from django.db import models
from rh.models import Escola

class UnidadeMedida(models.Model):
    """
    Representa a unidade de medida do produto.
    Ex.: Quilograma (kg), Litro (L), Unidade (un)
    """

    nome = models.CharField(
        max_length=50,
        unique=True
    )

    sigla = models.CharField(
        max_length=10,
        unique=True
    )

    class Meta:
        verbose_name = "Unidade de Medida"
        verbose_name_plural = "Unidades de Medida"
        ordering = ["nome"]

    def __str__(self):
        return self.sigla


class CategoriaProduto(models.Model):
    """
    Classificação do produto.
    Ex.: Alimentos, Material de Limpeza, Material Escolar
    """

    nome = models.CharField(
        max_length=100,
        unique=True
    )

    descricao = models.TextField(
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Categoria de Produto"
        verbose_name_plural = "Categorias de Produtos"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Produto(models.Model):
    """
    Cadastro central de produtos utilizados no sistema de estoque.
    Deve ser único e compartilhado entre todas as unidades escolares.
    """

    nome = models.CharField(
        max_length=150,
        help_text="Nome do produto (ex.: Arroz Branco Tipo 1)"
    )

    descricao = models.TextField(
        blank=True,
        null=True,
        help_text="Descrição detalhada do produto"
    )

    categoria = models.ForeignKey(
        CategoriaProduto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="produtos"
    )

    unidade_medida = models.ForeignKey(
        UnidadeMedida,
        on_delete=models.PROTECT,
        related_name="produtos"
    )

    codigo = models.CharField(
        max_length=50,
        unique=True,
        help_text="Código interno ou código do sistema de compras"
    )

    ativo = models.BooleanField(
        default=True,
        help_text="Indica se o produto está ativo para uso no sistema"
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["nome"]
        indexes = [
            models.Index(fields=["nome"]),
            models.Index(fields=["codigo"]),
        ]

    def __str__(self):
        return f"{self.nome} ({self.unidade_medida.sigla})"


class EstoqueGeral(models.Model):
    # Unidade escolar à qual o estoque pertence
    # Permite controlar o estoque de forma descentralizada por escola
    unidade_escolar = models.ForeignKey(
        Escola,
        on_delete=models.CASCADE,
        related_name="estoques"
    )

    # Produto armazenado no estoque (ex.: arroz, feijão, leite)
    # PROTECT impede exclusão do produto se houver registro em estoque
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name="movimentacoes_estoque"
    )

    # Data de fabricação do produto
    # Campo opcional, pois nem todo produto possui essa informação
    data_fabricacao = models.DateField(
        null=True,
        blank=True
    )

    # Data de validade do produto
    # Fundamental para controle de vencimentos e alertas
    data_validade = models.DateField(
        null=True,
        blank=True
    )

    # Data em que o produto entrou no estoque da unidade
    # Usada para rastreamento e controle histórico
    data_entrada = models.DateField()

    # Quantidade atual disponível do produto em estoque
    # Utiliza DecimalField para evitar erros de arredondamento
    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # Situação atual do item em estoque
    # Ex.: "Disponível", "Vencido", "Baixo estoque", "Bloqueado"
    situacao = models.CharField(
        max_length=50,
        blank=True
    )

    # Lote do produto
    # Importante para rastreabilidade e controle sanitário
    lote = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    # Ano de exercício do estoque
    # Facilita relatórios anuais e prestação de contas
    exercicio = models.PositiveIntegerField(
        help_text="Ano de referência do estoque"
    )

    # Data em que foi realizada a apuração ou conferência do estoque
    # Pode representar inventário físico ou fechamento mensal
    data_apuracao = models.DateField()

    # Observações gerais sobre o item em estoque
    # Campo livre para registros administrativos
    observacoes = models.TextField(
        blank=True,
        null=True
    )

    # Data e hora de criação do registro
    # Importante para auditoria
    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    # Data e hora da última atualização do registro
    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Controle de Estoque Geral"
        verbose_name_plural = "Controle de Estoque Geral"
        ordering = ["produto__nome"]

    def __str__(self):
        return (
            f"{self.produto} - "
            f"{self.quantidade} {self.produto.unidade_medida.sigla} "
            f"({self.unidade_escolar})"
        )
