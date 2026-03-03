
from django.db import models
from django.utils import timezone
from datetime import timedelta

# merendaEscolar/services/estoque_service.py

from admin_acessos.models import Notificacao
from django.db.models import Sum
from merendaEscolar.models import EstoqueEscola, Produto

def verificar_estoque_baixo(escola):
    saldos = (
        EstoqueEscola.objects
        .filter(escola=escola)
        .values("produto")
        .annotate(total=Sum("quantidade"))
    )

    for item in saldos:
        produto = Produto.objects.get(pk=item["produto"])
        total = item["total"] or 0

        if produto.estoque_minimo and total <= produto.estoque_minimo:

            ja_existe = Notificacao.objects.filter(
                escola=escola,
                tipo="ESTOQUE_BAIXO",
                lida=False,
                referencia_id=produto.id  # 👈 altamente recomendado
            ).exists()

            if not ja_existe:
                Notificacao.objects.create(
                    usuario=escola.responsavel,
                    escola=escola,
                    titulo="Estoque Baixo Detectado",
                    mensagem=(
                        f"O produto '{produto.nome}' está com saldo {total} "
                        f"{produto.unidade_medida.sigla}, "
                        f"abaixo do mínimo configurado ({produto.estoque_minimo})."
                    ),
                    tipo="ESTOQUE_BAIXO",
                    referencia_id=produto.id
                )


class EstoqueCentralQuerySet(models.QuerySet):

    def ativos(self):
        """Retorna apenas lotes com quantidade maior que zero."""
        return self.filter(quantidade__gt=0)

    def vencendo_em(self, dias=30):
        """Retorna produtos que vencem dentro do intervalo informado."""
        hoje = timezone.now().date()
        limite = hoje + timedelta(days=dias)

        return self.ativos().filter(
            data_validade__isnull=False,
            data_validade__gte=hoje,
            data_validade__lte=limite
        ).order_by("data_validade")

    def vencidos(self):
        hoje = timezone.now().date()
        return self.ativos().filter(
            data_validade__lt=hoje
        ).order_by("data_validade")

    def ordenado_por_validade(self):
        return self.ativos().order_by("data_validade", "produto__nome")
    




    # merendaEscolar/services.py

from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from merendaEscolar.models import ExecucaoReceita, EstoqueEscola, MovimentacaoEstoque
from django.db.models import F

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

