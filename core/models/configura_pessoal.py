from django.db import models

class ConfiguraPessoal(models.Model):
    pagina_CardapiosEscolares = models.IntegerField(default=5, verbose_name="Lista de Cardápios")

    