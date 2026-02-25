
from django.db import models
from django.utils import timezone
from datetime import timedelta


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

