from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from ...models import Transferencia

from core.models import ConfiguraPessoal
from core.views.baseNutricionista import BaseNutricionistaView

class TransferenciaListView(BaseNutricionistaView, ListView):
    model = Transferencia
    template_name = "merendaEscolar/transferencia/transferencia_list.html"
    context_object_name = "transferencias"

    # Faz com o que os dados de configuração sejam carregados antes de todo o conteudo da view
    def dispatch(self, request, *args, **kwargs):
        self.configuracao, _ = ConfiguraPessoal.objects.get_or_create(pk=1)
        return super().dispatch(request, *args, **kwargs)

    # Define a quantidade de registros na tela
    def get_paginate_by(self, queryset):
        return self.configuracao.pagina_transferencia   
    

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("escola_destino", "criado_por")
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pagina_transferencia"] = self.configuracao.pagina_transferencia   
        # 🔷 Fonte única de verdade (governança)
        context["page_size_options"] = [5, 10, 20, 30, 50]

        return context
