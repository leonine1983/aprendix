from controle_estoque.models import Movimentacao_Estoque
from controle_estoque.form import FornecedorForm
from django.utils.safestring import mark_safe
from django.views.generic import ListView




class MovimentoEstoque_ListView(ListView):
    model = Movimentacao_Estoque
    template_name = 'controle_estoque/movimentacao_estoque/movi_lista.html'


    def get_context_data(self, **kwargs):
        svg = '<svg class="bi" width="30" height="24" role="img" aria-label="Products"><use xlink:href="#grid"></use></svg>'
        context = super().get_context_data(**kwargs)
        context["svg"] = mark_safe(svg)
        context["title"] = 'Movimentação de Estoque'
        context ['active'] = 'movi'
        context ['fornecedor'] = 'cadastro'
        return context