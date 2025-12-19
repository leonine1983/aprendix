from django.contrib import admin
from .models import ComposicaoNotas, PlanejamentoKanban, ColunaKanban, MuralPost, MuralComentario
"""
admin.site.register(ComposicaoNotas)
@admin.register(Presenca)
class FrequenciaAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'data', 'presente')
"""
admin.site.register(PlanejamentoKanban)
admin.site.register(ColunaKanban)
admin.site.register(MuralPost)
admin.site.register(MuralComentario)