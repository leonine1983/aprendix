from django.db import models

class ConfiguraPessoal(models.Model):
    # Numero de registros por pagina
    pagina_CardapiosEscolares = models.IntegerField(default=5, verbose_name="Lista de Cardápios", null=True, blank=True)
    pagina_transferencia = models.IntegerField(default=5, verbose_name="Lista de Cardápios", null=True, blank=True)
    pagina_cardapioXescola = models.IntegerField(default=5, verbose_name="Lista de Cardápios", null=True, blank=True)
    pagina_receitas = models.IntegerField(default=5, verbose_name="Lista de Cardápios", null=True, blank=True)
    pagina_dashboardEscola = models.IntegerField(default=5, verbose_name="Lista de Cardápios", null=True, blank=True)
    pagina_estoqueCentral = models.IntegerField(default=5, verbose_name="Lista de Cardápios", null=True, blank=True)

    