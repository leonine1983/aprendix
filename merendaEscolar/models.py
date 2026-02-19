from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from rh.models import Escola
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator


User = get_user_model()


# ==============================
# MODELOS BÁSICOS DE CATEGORIA
# ==============================

class UnidadeMedida(models.Model):
    """
    Representa as unidades de medida dos produtos.
    Ex.: kg, litro, unidade.
    Usado em Produto para definir a medida de cada item.
    """
    nome = models.CharField(max_length=50, unique=True)
    sigla = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name = "Unidade de Medida"
        verbose_name_plural = "Unidades de Medida"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.sigla})"


class CategoriaProduto(models.Model):
    """
    Agrupamento de produtos por categoria.
    Ex.: Cereais, Carnes, Hortifrúti.
    Facilita relatórios, filtros e organização do estoque.
    """
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Categoria de Produto"
        verbose_name_plural = "Categorias de Produtos"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


# ==============================
# SEQUÊNCIAS PARA CONTROLE DE CÓDIGOS
# ==============================

class SequenciaProduto(models.Model):
    """
    Controla a sequência anual de códigos de produtos.
    Garante que cada produto criado recebe um código único,
    sem depender de dados existentes e evitando duplicidade.
    """
    ano = models.IntegerField(unique=True)
    ultimo_numero = models.IntegerField(default=0)


class SequenciaTransferencia(models.Model):
    """
    Controla a sequência anual de números de transferências.
    Garante numeração sequencial e auditável para cada transferência.
    """
    ano = models.IntegerField(unique=True)
    ultimo_numero = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Sequência de Transferência"
        verbose_name_plural = "Sequências de Transferência"


# ==============================
# MODELO PRINCIPAL DE PRODUTO
# ==============================

class Produto(models.Model):
    """
    Representa os produtos do estoque.
    Ex.: Arroz Branco Tipo 1.
    - Relaciona-se com CategoriaProduto e UnidadeMedida.
    - Recebe código sequencial anual via SequenciaProduto.
    """
    nome = models.CharField(max_length=150, help_text="Ex.: Arroz Branco Tipo 1")
    descricao = models.TextField(blank=True, null=True)
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
    codigo = models.CharField(max_length=20, unique=True, editable=False)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]
        indexes = [
            models.Index(fields=["nome"]),
            models.Index(fields=["codigo"]),
            models.Index(fields=["ativo"]),
        ]

    def __str__(self):
        return f"{self.nome} ({self.unidade_medida.sigla})"

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = self._gerar_codigo_sequencial()
        super().save(*args, **kwargs)

    def _gerar_codigo_sequencial(self):
        """
        Gera código do produto no formato PRD-ANO-XXXXX.
        Usa SequenciaProduto para evitar duplicidade e gaps.
        """
        ano = timezone.now().year
        with transaction.atomic():
            seq, _ = SequenciaProduto.objects.select_for_update().get_or_create(ano=ano)
            seq.ultimo_numero += 1
            seq.save()
            return f"PRD-{ano}-{seq.ultimo_numero:05d}"


# ==============================
# ESTOQUE
# ==============================

class EstoqueCentral(models.Model):
    """
    Estoque principal da instituição.
    Cada produto pode ter vários lotes.
    Usado para controlar entrada e saída central de produtos.
    """
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name="estoque_central")
    lote = models.CharField(max_length=50, blank=True, null=True)
    data_validade = models.DateField(blank=True, null=True)
    quantidade = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["produto", "lote"], name="unique_produto_lote_central")
        ]

    def __str__(self):
        return f"{self.produto.nome} - Lote {self.lote or 'Sem lote'}"


class EstoqueEscola(models.Model):
    """
    Estoque de cada escola.
    Recebe produtos do EstoqueCentral via Transferência.
    Permite controle individual por escola e lote.
    """
    escola = models.ForeignKey(Escola, on_delete=models.CASCADE, related_name="estoque_escola")
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    lote = models.CharField(max_length=50, blank=True, null=True)
    quantidade = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["escola", "produto", "lote"], name="unique_escola_produto_lote")
        ]


# ==============================
# MOVIMENTAÇÃO DE ESTOQUE
# ==============================

class MovimentacaoEstoque(models.Model):
    """
    Registra entradas e saídas de produtos, seja do estoque central ou das escolas.
    Tipos:
        - ENTRADA_CENTRAL / SAIDA_CENTRAL
        - ENTRADA_ESCOLA / SAIDA_ESCOLA
        - AJUSTE (manual)
    """
    TIPO_CHOICES = (
        ("ENTRADA_CENTRAL", "Entrada Central"),
        ("SAIDA_CENTRAL", "Saída Central"),
        ("ENTRADA_ESCOLA", "Entrada Escola"),
        ("SAIDA_ESCOLA", "Saída Escola"),
        ("AJUSTE", "Ajuste Manual"),
    )

    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    escola = models.ForeignKey(Escola, on_delete=models.SET_NULL, null=True, blank=True)
    quantidade = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    data_movimentacao = models.DateTimeField(auto_now_add=True)
    observacao = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-data_movimentacao"]
        indexes = [
            models.Index(fields=["produto"]),
            models.Index(fields=["tipo"]),
            models.Index(fields=["data_movimentacao"]),
        ]

    def clean(self):
        if "ESCOLA" in self.tipo and not self.escola:
            raise ValidationError("Movimentações de escola exigem escola definida.")


# ==============================
# TRANSFERÊNCIAS DE ESTOQUE
# ==============================

class Transferencia(models.Model):
    """
    Representa o envio de produtos do estoque central para uma escola.
    Cada transferência recebe número único anual via SequenciaTransferencia.
    """
    numero = models.CharField(max_length=30, unique=True, editable=False)
    escola_destino = models.ForeignKey(Escola, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=20,
        choices=(("RASCUNHO", "Rascunho"), ("ENVIADO", "Enviado"), ("RECEBIDO", "Recebido")),
        default="RASCUNHO"
    )
    criado_por = models.ForeignKey(User, on_delete=models.PROTECT)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self._gerar_numero_transferencia()
        super().save(*args, **kwargs)

    def _gerar_numero_transferencia(self):
        """
        Gera número da transferência no formato TRF-ANO-XXXXX.
        Usa SequenciaTransferencia para evitar duplicidade.
        """
        ano = timezone.now().year
        with transaction.atomic():
            seq, _ = SequenciaTransferencia.objects.select_for_update().get_or_create(ano=ano)
            seq.ultimo_numero += 1
            seq.save()
            return f"TRF-{ano}-{seq.ultimo_numero:05d}"


class TransferenciaItem(models.Model):
    """
    Produtos específicos incluídos em uma Transferência.
    Cada produto só pode aparecer uma vez por transferência.
    """
    transferencia = models.ForeignKey(Transferencia, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["transferencia", "produto"], name="unique_produto_por_transferencia")
        ]


# ==============================
# DIVERGÊNCIAS DE ENTREGA
# ==============================

class DivergenciaEntrega(models.Model):
    """
    Registrada exclusivamente pela escola no ato do recebimento.
    O sistema NÃO cria automaticamente.
    A escola informa a quantidade realmente recebida.
    """

    STATUS_CHOICES = (
        ("ABERTA", "Aberta"),
        ("EM_ANALISE", "Em Análise"),
        ("CONFIRMADA", "Confirmada"),
        ("INDEFERIDA", "Indeferida"),
        ("RESOLVIDA", "Resolvida"),
    )

    transferencia = models.ForeignKey(
        Transferencia,
        on_delete=models.CASCADE,
        related_name="divergencias"
    )

    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT
    )

    quantidade_enviada = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    quantidade_recebida = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    descricao = models.TextField(
        help_text="Descreva detalhadamente a divergência identificada."
    )

    registrado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="divergencias_registradas"
    )

    confirmado_transporte = models.BooleanField(
        default=False,
        help_text="Transporte confirma a veracidade da divergência."
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ABERTA"
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-criado_em"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["criado_em"]),
        ]

    def clean(self):
        """
        Validação institucional:
        Só existe divergência se a quantidade recebida for diferente da enviada.
        """
        if self.quantidade_recebida == self.quantidade_enviada:
            raise ValidationError("Não há divergência se as quantidades forem iguais.")

    @property
    def diferenca(self):
        return self.quantidade_enviada - self.quantidade_recebida

    def __str__(self):
        return f"Divergência - {self.transferencia.numero} - {self.produto.nome}"
