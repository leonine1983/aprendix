from controle_estoque.models import ProgramacaoSaidaEstoque
from controle_estoque.form import FornecedorForm
from django.utils.safestring import mark_safe
from django.views.generic import DetailView




class ProgramaEstoque_Ver_detailView(DetailView):
    model = ProgramacaoSaidaEstoque
    template_name = 'controle_estoque/programa_estoque/program_lista.html'
    context_object_name = 'programacao'


    def get_context_data(self, **kwargs):
        svg = '<svg class="bi" width="30" height="24" role="img" aria-label="Products"><use xlink:href="#grid"></use></svg>'
        context = super().get_context_data(**kwargs)
        context["svg"] = mark_safe(svg)
        context["title"] = 'DETALHADO: Programação de Saída do dia'
        context ['active'] = 'program'
        context ['fornecedor'] = 'cadastro'
        return context