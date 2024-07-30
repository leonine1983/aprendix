from controle_estoque.models import Prefeitura
from django.views.generic import ListView

class Prefeitura_View (ListView):
    model = Prefeitura
    template_name = 'controle_estoque/prefeitura/prefeitura_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        # Exibe o menu no contexto que está sendo solicitado
        context ['active'] = 'prefeitura'
        # Habilitar a versão ativa do menu
        context ['fornecedor'] = 'lista'

        return context