"""
Módulo: cozinha/models.py

Responsável por registrar a execução de receitas nas cozinhas escolares
e o consumo/devolução de ingredientes do estoque.

Possui duas responsabilidades principais:

1) Registro da execução de receitas
2) Movimentação interna da cozinha (retirada/devolução)

Toda alteração de estoque ocorre dentro de TRANSAÇÕES ATÔMICAS
para evitar inconsistência em ambientes com múltiplos usuários.
"""

# =========================================================
# IMPORTS DJANGO
# =========================================================

from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

# =========================================================
# IMPORTS TERCEIROS
# =========================================================

from ckeditor.fields import RichTextField

# =========================================================
# IMPORTS INTERNOS DO PROJETO
# =========================================================

from rh.models import Escola

from merendaEscolar.models import (
    Produto,
    Receita,
    EstoqueEscola,
    MovimentacaoEstoque,
)

# =========================================================
# USER MODEL
# =========================================================

User = get_user_model()


# =========================================================
# MODELO: MOVIMENTAÇÃO DA COZINHA
# =========================================================

class MovimentacaoCozinha(models.Model):
    """
    Registra movimentações internas da cozinha.

    Diferença importante:
    - MovimentacaoEstoque → controla o estoque oficial
    - MovimentacaoCozinha → registra o uso na cozinha

    Isso permite auditoria completa da merenda escolar.
    """

    TIPO_CHOICES = (
        ("RETIRADA_RECEITA", "Retirada para Receita"),
        ("RETIRADA_EXTRA", "Retirada Extra"),
        ("DEVOLUCAO", "Devolução ao Estoque"),
    )

    escola = models.ForeignKey(
        Escola,
        on_delete=models.CASCADE
    )

    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT
    )

    lote = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    quantidade = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )

    execucao_receita = models.ForeignKey(
        "ExecucaoReceitaCozinha",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    observacao = RichTextField(
        blank=True,
        null=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.produto} - {self.tipo} - {self.quantidade}"


# =========================================================
# MODELO: EXECUÇÃO DE RECEITA NA COZINHA
# =========================================================

class ExecucaoReceitaCozinha(models.Model):
    """
    Representa a execução real de uma receita na cozinha.

    Exemplo:
    Receita: "Arroz com frango"
    Execução: Preparação feita na escola em determinado dia.
    """

    STATUS = (
        ("ABERTA", "Aberta"),
        ("EM_PREPARO", "Em preparo"),
        ("FINALIZADA", "Finalizada"),
        ("CANCELADA", "Cancelada"),
    )

    escola = models.ForeignKey(
        Escola,
        on_delete=models.PROTECT
    )

    receita = models.ForeignKey(
        Receita,
        on_delete=models.PROTECT
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="ABERTA"
    )

    iniciado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )

    iniciado_em = models.DateTimeField(
        auto_now_add=True
    )

    finalizado_em = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ["-iniciado_em"]

    def __str__(self):
        return f"{self.receita.nome} - {self.escola}"


# =========================================================
# SERVIÇO DE DOMÍNIO: RETIRAR INGREDIENTE PARA RECEITA
# =========================================================

@transaction.atomic
def retirar_ingrediente_receita(execucao, produto, quantidade, usuario):
    """
    Realiza retirada de ingredientes do estoque da escola
    para uso em uma execução de receita.

    Estratégia usada:
    FEFO (First Expire First Out)
    → consome primeiro os lotes que vencem antes.

    select_for_update() garante que os registros
    fiquem bloqueados durante a operação.
    """

    lotes = (
        EstoqueEscola.objects
        .select_for_update()
        .filter(
            escola=execucao.escola,
            produto=produto,
            quantidade__gt=0
        )
        .order_by("data_validade")
    )

    restante = quantidade

    for lote in lotes:

        if restante <= 0:
            break

        consumir = min(lote.quantidade, restante)

        # reduz quantidade no lote
        lote.quantidade -= consumir
        lote.save()

        # registra saída no estoque oficial
        MovimentacaoEstoque.objects.create(
            produto=produto,
            escola=execucao.escola,
            quantidade=consumir,
            tipo="SAIDA_ESCOLA",
            usuario=usuario,
            observacao=f"Retirada para receita {execucao.receita.nome}"
        )

        # registra movimentação interna da cozinha
        MovimentacaoCozinha.objects.create(
            escola=execucao.escola,
            produto=produto,
            lote=lote.lote,
            quantidade=consumir,
            tipo="RETIRADA_RECEITA",
            usuario=usuario,
            execucao_receita=execucao
        )

        restante -= consumir

    if restante > 0:
        raise ValidationError("Estoque insuficiente.")


# =========================================================
# SERVIÇO DE DOMÍNIO: DEVOLVER INGREDIENTE AO ESTOQUE
# =========================================================

@transaction.atomic
def devolver_ingrediente(execucao, produto, lote, quantidade, usuario):
    """
    Realiza devolução de ingredientes não utilizados
    da cozinha para o estoque da escola.
    """

    estoque, _ = (
        EstoqueEscola.objects
        .select_for_update()
        .get_or_create(
            escola=execucao.escola,
            produto=produto,
            lote=lote,
            defaults={"quantidade": 0}
        )
    )

    estoque.quantidade += quantidade
    estoque.save()

    # registra entrada no estoque oficial
    MovimentacaoEstoque.objects.create(
        produto=produto,
        escola=execucao.escola,
        quantidade=quantidade,
        tipo="ENTRADA_ESCOLA",
        usuario=usuario,
        observacao=f"Devolução da cozinha - receita {execucao.receita.nome}"
    )

    # registra movimentação da cozinha
    MovimentacaoCozinha.objects.create(
        escola=execucao.escola,
        produto=produto,
        lote=lote,
        quantidade=quantidade,
        tipo="DEVOLUCAO",
        usuario=usuario,
        execucao_receita=execucao
    )

"""
Fluxo operacional real da merendeira
1️⃣ Merendeira abre receita do dia
        ↓
2️⃣ Sistema mostra ingredientes
        ↓
3️⃣ Merendeira retira ingredientes do estoque
        ↓
4️⃣ Se precisar mais → RETIRADA EXTRA
        ↓
5️⃣ Se sobrar → DEVOLUÇÃO
        ↓
6️⃣ Finaliza preparo
"""