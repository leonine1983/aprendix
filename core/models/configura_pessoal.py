from django.db import models
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ConfiguraPessoal(models.Model):
    # Usuário dono da configuração
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="configuracao_pessoal",
        verbose_name="Usuário"
    )

    # Número de registros por página
    pagina_CardapiosEscolares = models.IntegerField(
        default=5,
        verbose_name="Lista de Cardápios",
        null=True,
        blank=True
    )

    pagina_transferencia = models.IntegerField(
        default=5,
        verbose_name="Lista de Transferências",
        null=True,
        blank=True
    )

    pagina_cardapioXescola = models.IntegerField(
        default=5,
        verbose_name="Cardápio por Escola",
        null=True,
        blank=True
    )

    pagina_receitas = models.IntegerField(
        default=5,
        verbose_name="Lista de Receitas",
        null=True,
        blank=True
    )

    pagina_dashboardEscola = models.IntegerField(
        default=5,
        verbose_name="Dashboard da Escola",
        null=True,
        blank=True
    )

    pagina_estoqueCentral = models.IntegerField(
        default=5,
        verbose_name="Estoque Central",
        null=True,
        blank=True
    )

    pagina_movimentacaoEstoque = models.IntegerField(
        default=5,
        verbose_name="Movimentação de Estoque",
        null=True,
        blank=True
    )

    # App Merendeiras
    pagina_ExecutaReceitas = models.IntegerField(
        default=5,
        verbose_name="Execução de Receitas",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Configuração Pessoal"
        verbose_name_plural = "Configurações Pessoais"

    def __str__(self):
        return f"Configurações de {self.usuario.get_username()}"

    