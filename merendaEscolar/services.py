
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

