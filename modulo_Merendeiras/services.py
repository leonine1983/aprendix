# merendaEscolar/services.py

from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from merendaEscolar.models import ExecucaoReceita, EstoqueEscola, MovimentacaoEstoque
from django.db.models import F
from merendaEscolar.models import Receita
from modulo_Merendeiras.models import ExecucaoCardapioDia
from modulo_Merendeiras.models import (ExecucaoCardapioDia, executar_cardapio_do_dia, verificar_disponibilidade_ingredientes)


@transaction.atomic
def executar_receita(execucao: ExecucaoReceita, usuario):
    """
    Executa a receita de forma institucional:
    - Abate estoque da escola automaticamente
    - Gera Movimentacoes auditáveis
    - Garante execução apenas uma vez
    """

    if execucao.status != "PLANEJADA":
        raise ValidationError("Receita já executada ou cancelada.")

    hoje = timezone.now().date()
    escola = execucao.escola

    # Itera por cada ingrediente
    for ingrediente in execucao.receita.ingredientes.select_related("produto"):

        quantidade_necessaria = ingrediente.quantidade

        # Busca lotes da escola ordenados por validade (FEFO)
        lotes = (
            EstoqueEscola.objects
            .select_for_update()
            .filter(
                escola=escola,
                produto=ingrediente.produto,
                quantidade__gt=0
            )
            .order_by("data_validade")  # FEFO real
        )

        if not lotes.exists():
            raise ValidationError(
                f"Não há estoque disponível do produto {ingrediente.produto.nome}"
            )

        for lote in lotes:

            if quantidade_necessaria <= 0:
                break

            consumir = min(lote.quantidade, quantidade_necessaria)
            lote.quantidade = F('quantidade') - consumir
            lote.save(update_fields=['quantidade', 'atualizado_em'])

            # Movimentação auditável
            MovimentacaoEstoque.objects.create(
                produto=lote.produto,
                escola=escola,
                quantidade=consumir,
                tipo="SAIDA_ESCOLA",
                usuario=usuario,
                observacao=f"Execução da receita {execucao.receita.nome} - Lote {lote.lote or 'Sem Lote'}"
            )

            quantidade_necessaria -= consumir

        if quantidade_necessaria > 0:
            raise ValidationError(
                f"Estoque insuficiente para o produto {ingrediente.produto.nome}"
            )

    execucao.status = "EXECUTADA"
    execucao.executada_por = usuario
    execucao.data_execucao = hoje
    execucao.save(update_fields=["status", "executada_por", "data_execucao"])




