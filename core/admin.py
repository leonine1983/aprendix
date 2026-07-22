from django.contrib import admin
from .models.perfil import *
from .models.configura_pessoal import ConfiguraPessoal

# Register your models here.
admin.site.register(PerfilUsuario)
admin.site.register(ConfiguraPessoal)