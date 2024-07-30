from controle_estoque.models import Prefeitura
from django.views.generic import UpdateView
from django.urls import reverse_lazy


class Prefeitura_Update (UpdateView):
    model = Prefeitura
    fields = ['instituto', 'endereco', 'pessoa_publica', 'nutricionista1', 'cfn1', 'nutricionista2', 'cfn2']
    template_name = 'controle_estoque/prefeitura/prefeitura_cadastro.html'
    success_url = reverse_lazy('controle_estoque:prefeitura_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        # Exibe o menu no contexto que está sendo solicitado
        context ['active'] = 'prefeitura'
        # Habilitar a versão ativa do menu
        context ['fornecedor'] = 'update'
        context['mostra_icone'] = 'prefeitura_update'

        return context