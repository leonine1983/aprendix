from django.contrib import admin
from .models import ComposicaoNotas
from gestao_escolar.models import Presenca

admin.site.register(ComposicaoNotas)
@admin.register(Presenca)
class FrequenciaAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'data', 'presente')
