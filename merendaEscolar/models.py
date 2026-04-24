# models merendaEscolar
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from rh.models import Escola
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from ckeditor.fields import RichTextField


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
    descricao = RichTextField(
    blank=True,
    null=True,
    config_name="default",
    help_text="Descrição técnica da categoria alimentar."
)

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
    descricao = RichTextField(
    blank=True,
    null=True,
    config_name="default",
    help_text="Descrição técnica detalhada do produto."
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
    codigo = models.CharField(max_length=20, unique=True, editable=False)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    estoque_minimo = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        help_text="Quantidade mínima aceitável no estoque da escola."
    )

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

from django.db.models import Case, When, Value, IntegerField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
from django.utils import timezone
from django.db.models import Case, When, Value, IntegerField


class EstoqueCentralQuerySet(models.QuerySet):

    def ordenado_por_validade(self):
        hoje = timezone.now().date()

        return (
            self.annotate(
                prioridade_validade=Case(
                    # Vencido
                    When(data_validade__lt=hoje, then=Value(0)),

                    # Crítico: até 7 dias
                    When(
                        data_validade__gte=hoje,
                        data_validade__lte=hoje + timedelta(days=7),
                        then=Value(1)
                    ),

                    # Alerta: 8 a 30 dias
                    When(
                        data_validade__gt=hoje + timedelta(days=7),
                        data_validade__lte=hoje + timedelta(days=30),
                        then=Value(2)
                    ),

                    # Normal (mais de 30 dias)
                    When(data_validade__gt=hoje + timedelta(days=30), then=Value(3)),

                    # Sem validade
                    default=Value(4),

                    output_field=IntegerField(),
                )
            )
            .order_by("prioridade_validade", "data_validade")
        )

class EstoqueCentral(models.Model):
    """
    Estoque principal da instituição.
    Cada produto pode ter vários lotes.
    Usado para controlar entrada e saída central de produtos.
    """

    objects = EstoqueCentralQuerySet.as_manager()

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
    
    @property
    def status_validade(self):
        hoje = timezone.now().date()

        if not self.data_validade:
            return "SEM_VALIDADE"

        dias = (self.data_validade - hoje).days

        if dias < 0:
            return "VENCIDO"
        elif dias <= 7:
            return "CRITICO"
        elif dias <= 30:
            return "ALERTA"
        return "NORMAL"


# Descarte de protudo
class DescarteEstoque(models.Model):
    """
    Registro institucional de descarte de produtos do estoque.
    Usado para baixa sanitária de itens vencidos ou impróprios para consumo.
    """

    MOTIVO_CHOICES = (
        ("VENCIDO", "Produto Vencido"),
        ("MOFO", "Produto Mofado"),
        ("GORGULHO", "Infestação (gorgulho ou insetos)"),
        ("EMBALAGEM_DANIFICADA", "Embalagem Danificada"),
        ("CONTAMINACAO", "Contaminação"),
        ("OUTRO", "Outro Motivo"),
    )

    estoque = models.ForeignKey(
        EstoqueCentral,
        on_delete=models.PROTECT,
        related_name="descartes"
    )

    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT
    )

    quantidade = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    motivo = models.CharField(
        max_length=30,
        choices=MOTIVO_CHOICES
    )

    descricao = RichTextField(
        blank=True,
        null=True,
        config_name="minimal",
        help_text="Descrição complementar do descarte."
    )

    registrado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Descarte - {self.produto.nome}"



########### ESCOLA ###############################
class EstoqueEscola(models.Model):

    escola = models.ForeignKey(Escola, on_delete=models.CASCADE, related_name="estoque_escola")

    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)

    lote = models.CharField(max_length=50, blank=True, null=True)

    data_validade = models.DateField(blank=True, null=True)

    quantidade = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Lote:  {self.lote} - {self.escola}"

    class Meta:
        ordering = ["data_validade"]   # ← aqui
        constraints = [
            models.UniqueConstraint(
                fields=["escola", "produto", "lote"],
                name="unique_escola_produto_lote"
            )
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
    observacao = RichTextField(
    blank=True,
    null=True,
    config_name="minimal"
)

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
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.tipo in ["ENTRADA_ESCOLA", "SAIDA_ESCOLA"] and self.escola:
            from merendaEscolar.services import verificar_estoque_baixo
            verificar_estoque_baixo(self.escola)


# ==============================
# TRANSFERÊNCIAS DE ESTOQUE
# ==============================

class Transferencia(models.Model):
    """
    Representa o envio de produtos do estoque central para uma escola.
    Cada transferência recebe número único anual via SequenciaTransferencia.
    """
    numero = models.CharField(max_length=30, unique=True, editable=False)
    escola_destino = models.ForeignKey(Escola, related_name='escola_confirma_transf', on_delete=models.PROTECT)
    status = models.CharField(
                                    max_length=20,
                                    choices=(
                                        ("RASCUNHO", "Rascunho"),
                                        ("ENVIADO", "Enviado"),
                                        ("EM_CONFERENCIA", "Em Conferência"),
                                        ("RECEBIDO", "Recebido"),
                                    ),
                                    default="RASCUNHO"
                                )
    criado_por = models.ForeignKey(User, on_delete=models.PROTECT)
    criado_em = models.DateTimeField(auto_now_add=True)

    enviado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="transferencias_enviadas"
    )

    enviado_em = models.DateTimeField(
        null=True,
        blank=True
    )

    recebido_por = models.ForeignKey(
    User,
    on_delete=models.PROTECT,
    null=True,
    blank=True,
    related_name="transferencias_recebidas"
    )

    recebido_em = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.numero} - {self.escola_destino}"


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

    @transaction.atomic
    def enviar(self, usuario):
        """
        Executa o envio institucional da transferência.

        Regras aplicadas:
        - Apenas transferências em RASCUNHO podem ser enviadas.
        - Deve existir ao menos um item.
        - Cada item deve possuir saldo suficiente no lote selecionado.
        - A baixa ocorre exatamente no lote de origem.
        - Gera movimentações de saída com identificação do lote.
        - Atualiza o status para ENVIADO.

        Garantias técnicas:
        - Operação transacional (atomic).
        - Bloqueio pessimista de estoque (select_for_update).
        - Rastreabilidade sanitária por lote.
        """
        from django.utils import timezone

        if self.status != "RASCUNHO":
            raise ValidationError("Apenas transferências em rascunho podem ser enviadas.")

        if not self.itens.exists():
            raise ValidationError("Não é permitido enviar transferência sem itens.")

        for item in self.itens.select_related("estoque_origem"):

            estoque = (
                EstoqueCentral.objects
                .select_for_update()
                .get(pk=item.estoque_origem.pk)
            )

            if estoque.quantidade < item.quantidade:
                raise ValidationError(
                    f"Saldo insuficiente no lote {estoque.lote} "
                    f"do produto {estoque.produto.nome}."
                )

        for item in self.itens.select_related("estoque_origem"):

            estoque = item.estoque_origem
            estoque.quantidade -= item.quantidade
            estoque.save()

            MovimentacaoEstoque.objects.create(
                produto=estoque.produto,
                quantidade=item.quantidade,
                tipo="SAIDA_CENTRAL",
                usuario=usuario,
                observacao=f"Transferência {self.numero} - Lote {estoque.lote}"
            )

        self.status = "ENVIADO"
        self.enviado_por = usuario
        self.enviado_em = timezone.now()
        self.save()
        
    @transaction.atomic
    def receber(self, usuario):
        """
        Confirma o recebimento institucional da transferência.

        Regras aplicadas:
        - Apenas transferências em EM_CONFERENCIA podem ser recebidas.
        - Considera divergências registradas pela escola.
        - Atualiza estoque com a quantidade efetivamente recebida.
        - Gera movimentação de entrada rastreável.
        - Atualiza status para RECEBIDO.

        Garantias:
        - Operação transacional.
        - Bloqueio pessimista do estoque da escola.
        - Integridade contábil e auditável.
        """

        if self.status != "EM_CONFERENCIA":
            raise ValidationError(
                "A transferência deve estar em conferência para ser recebida."
            )

        for item in self.itens.select_related("produto"):

            # Verifica se existe divergência registrada para o produto
            divergencia = (
                self.divergencias
                .filter(produto=item.produto)
                .first()
            )

            # Define quantidade final a ser lançada no estoque
            if divergencia:
                quantidade_final = divergencia.quantidade_recebida
            else:
                quantidade_final = item.quantidade

            # Atualiza estoque da escola com lock
            estoque_escola, _ = EstoqueEscola.objects.select_for_update().get_or_create(
            escola=self.escola_destino,
            produto=item.produto,
            lote=item.estoque_origem.lote,
            defaults={
                "quantidade": 0,
                "data_validade": item.estoque_origem.data_validade
            }
            )

            estoque_escola.quantidade += quantidade_final
            estoque_escola.save()

            # Gera movimentação auditável
            MovimentacaoEstoque.objects.create(
                produto=item.produto,
                escola=self.escola_destino,
                quantidade=quantidade_final,
                tipo="ENTRADA_ESCOLA",
                usuario=usuario,
                observacao=f"Recebimento da Transferência {self.numero}"
            )

        from django.utils import timezone

        self.status = "RECEBIDO"
        self.recebido_por = usuario
        self.recebido_em = timezone.now()
        self.save()

    def delete(self, *args, **kwargs):
        """
        Impede exclusão de transferências já enviadas ou recebidas.

        Apenas transferências em RASCUNHO podem ser excluídas,
        garantindo rastreabilidade e segurança jurídica.
        """

        if self.status != "RASCUNHO":
            raise ValidationError(
                "Transferências enviadas ou recebidas não podem ser excluídas."
            )

        super().delete(*args, **kwargs)


class TransferenciaItem(models.Model):
    """
    Representa um item específico dentro de uma Transferência.

    Cada item referencia explicitamente um lote do EstoqueCentral
    (estoque_origem), garantindo rastreabilidade sanitária e contábil.

    Regras institucionais:
    - O lote selecionado deve pertencer ao produto informado.
    - Não é permitido alterar itens de transferências já enviadas.
    - A quantidade solicitada não pode exceder o saldo disponível no lote.
    - O mesmo lote não pode ser incluído mais de uma vez na mesma transferência.

    Essa modelagem garante:
    - Controle por lote (rastreabilidade sanitária).
    - Aplicação da estratégia FEFO (First Expire, First Out).
    - Integridade jurídica e auditável do fluxo logístico.
    """

    transferencia = models.ForeignKey(
        Transferencia,
        on_delete=models.CASCADE,
        related_name="itens"
    )

    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT
    )

    estoque_origem = models.ForeignKey(
        EstoqueCentral,
        on_delete=models.PROTECT,
        related_name="transferencias_itens"
    )

    quantidade = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["transferencia", "estoque_origem"],
                name="unique_lote_por_transferencia"
            )
        ]

    def clean(self):
        """
        Validação institucional do item de transferência.

        Regras aplicadas:
        - Transferências não podem ser alteradas após envio.
        - O lote selecionado deve pertencer ao produto informado.
        - A quantidade não pode exceder o saldo do lote.

        Implementação defensiva:
        - Nunca assume que FKs estão resolvidas.
        - Usa *_id antes de acessar relacionamentos.
        """

        super().clean()

        # Garantir que a transferência está presente
        if not self.transferencia_id:
            return  # CreateView ainda pode não ter vinculado

        # Bloqueio por status
        if self.transferencia.status != "RASCUNHO":
            raise ValidationError(
                "Não é permitido alterar itens de transferência já enviada."
            )

        # Garantir que campos essenciais existem antes de validar
        if not self.estoque_origem_id or not self.produto_id:
            return  # O próprio form validará obrigatoriedade

        # Validar coerência produto ↔ lote (comparando IDs)
        if self.estoque_origem.produto_id != self.produto_id:
            raise ValidationError(
                "O lote selecionado não pertence ao produto informado."
            )

        # Validar saldo
        if self.quantidade and self.quantidade > self.estoque_origem.quantidade:
            raise ValidationError(
                "Quantidade superior ao saldo disponível no lote."
            )

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


    descricao = RichTextField(
        help_text="Descreva detalhadamente a divergência identificada.",
        config_name="default"
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
    


################# RECEITA ##########################
####################################################
class Receita(models.Model):
    """
    Receita institucional proposta pela Secretaria.
    """
    nome = models.CharField(max_length=150)
    descricao = RichTextField()
    modo_preparo = RichTextField()
    ativa = models.BooleanField(default=True)
    
    # ADICIONAR ESTE CAMPO:
    rendimento = models.PositiveIntegerField(
        default=100,
        help_text="Quantidade de porções que a receita produz (padrão)"
    )

    criada_por = models.ForeignKey(User, on_delete=models.PROTECT)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome

   

class ReceitaIngrediente(models.Model):
    """
    Define os insumos necessários para preparar a receita.
    Representa a ficha técnica alimentar.
    """

    receita = models.ForeignKey(
        Receita,
        on_delete=models.CASCADE,
        related_name="ingredientes"
    )

    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)

    quantidade = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        unique_together = ("receita", "produto")


class ExecucaoReceita(models.Model):
    """
    Representa a execução real da receita pela escola.
    É aqui que ocorre o abatimento automático do estoque.
    """

    STATUS_CHOICES = (
        ("PLANEJADA", "Planejada"),
        ("EXECUTADA", "Executada"),
        ("CANCELADA", "Cancelada"),
    )

    receita = models.ForeignKey(Receita, on_delete=models.PROTECT)
    escola = models.ForeignKey(Escola, on_delete=models.PROTECT)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PLANEJADA")

    executada_por = models.ForeignKey(User, on_delete=models.PROTECT)
    data_execucao = models.DateField(default=timezone.now)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data_execucao"]


from django.db import transaction
from django.utils import timezone

@transaction.atomic
def executar_receita(execucao: ExecucaoReceita, usuario: User):

    if execucao.status != "PLANEJADA":
        raise ValidationError("Receita já executada ou cancelada.")

    hoje = timezone.now().date()

    for ingrediente in execucao.receita.ingredientes.select_related("produto"):

        quantidade_necessaria = ingrediente.quantidade

        # Buscar lotes da escola ordenados por validade (FEFO)
        lotes = (
            EstoqueEscola.objects
            .select_for_update()
            .filter(
                escola=execucao.escola,
                produto=ingrediente.produto,
                quantidade__gt=0
            )
            .order_by("data_validade", "lote")
        )

        # Recomendo fortemente adicionar esse campo para rastreabilidade sanitária.

        for lote in lotes:

            # Aqui você deverá validar vencimento quando incluir data_validade
            # if lote.data_validade < hoje:
            #     continue

            if quantidade_necessaria <= 0:
                break

            consumir = min(lote.quantidade, quantidade_necessaria)

            lote.quantidade -= consumir
            lote.save()

            MovimentacaoEstoque.objects.create(
                produto=lote.produto,
                escola=execucao.escola,
                quantidade=consumir,
                tipo="SAIDA_ESCOLA",
                usuario=usuario,
                observacao=f"Execução da receita {execucao.receita.nome}"
            )

            quantidade_necessaria -= consumir

        if quantidade_necessaria > 0:
            raise ValidationError(
                f"Estoque insuficiente para o produto {ingrediente.produto.nome}"
            )

    execucao.status = "EXECUTADA"
    execucao.save()


# PARTE DO CARDAPIO
class Cardapio(models.Model):
    """
    Representa o cardápio institucional (mensal ou período).
    Ex: Fundamental II - Março/2026
    """

    nome = models.CharField(max_length=150)
    descricao = RichTextField(
    blank=True,
    null=True,
    config_name="default",
    help_text="Descrição técnica do cardápio alimentar."
)

    data_inicio = models.DateField()
    data_fim = models.DateField()

    ativo = models.BooleanField(default=True)
    gerar_execucao = models.BooleanField(default=True)

    criado_por = models.ForeignKey(User, on_delete=models.PROTECT)
    criado_em = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.data_fim < self.data_inicio:
            raise ValidationError("Data fim não pode ser menor que data início.")
        
    class Meta:
        indexes = [
            models.Index(fields=["ativo"]),
            models.Index(fields=["data_inicio", "data_fim"]),
        ]

    def __str__(self):
        return self.nome
    
    
class CardapioSemana(models.Model):
    """
    Divide o cardápio em semanas (1ª, 2ª, etc.)
    """

    cardapio = models.ForeignKey(Cardapio, on_delete=models.CASCADE, related_name="semanas")
    numero = models.IntegerField()  # 1, 2, 3, 4...

    class Meta:
        unique_together = ("cardapio", "numero")

    def __str__(self):
        return f"Semana {self.numero} - {self.cardapio.nome}"
    

class CardapioDia(models.Model):
    """
    Representa o dia da semana dentro da semana do cardápio
    """

    DIAS_CHOICES = (
        (1, "Segunda"),
        (2, "Terça"),
        (3, "Quarta"),
        (4, "Quinta"),
        (5, "Sexta"),
    )

    semana = models.ForeignKey(CardapioSemana, on_delete=models.CASCADE, related_name="dias")
    dia_semana = models.IntegerField(choices=DIAS_CHOICES)

    class Meta:
        unique_together = ("semana", "dia_semana")

    def __str__(self):
        return f"{self.get_dia_semana_display()} - Semana {self.semana.numero}"
    

class TipoRefeicao(models.Model):
    nome = models.CharField(max_length=50, unique=True)    

    def __str__(self):
        return self.nome
    

class CardapioItem(models.Model):
    dia = models.ForeignKey(CardapioDia, on_delete=models.CASCADE, related_name="itens")
    tipo_refeicao = models.ForeignKey(TipoRefeicao, on_delete=models.PROTECT)
    receita = models.ForeignKey(Receita, on_delete=models.PROTECT)
    ordem = models.IntegerField(default=0)

    class Meta:
        ordering = ["ordem"]
        constraints = [
            models.UniqueConstraint(
                fields=["dia", "tipo_refeicao", "receita"],
                name="unique_receita_por_dia_refeicao"
            ),
            models.UniqueConstraint(
                fields=["dia", "tipo_refeicao", "ordem"],
                name="unique_ordem_por_refeicao"
            )
        ]


class CardapioEscola(models.Model):
    cardapio = models.ForeignKey(Cardapio, on_delete=models.CASCADE)
    escola = models.ForeignKey(Escola, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("cardapio", "escola")