from django.contrib import admin
from .models import ExecucaoReceitaCozinha, MovimentacaoCozinha, DescarteEstoqueEscola,ExecucaoCardapioDia,FichaExecucaoReceita

admin.site.register(ExecucaoReceitaCozinha)
admin.site.register(MovimentacaoCozinha)
admin.site.register(DescarteEstoqueEscola)
admin.site.register(ExecucaoCardapioDia)
admin.site.register(FichaExecucaoReceita)