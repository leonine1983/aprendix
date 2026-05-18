from controle_estoque.models import ProgramacaoSaidaEstoque
from .program_form import Program_saida_form
from django.utils.safestring import mark_safe
from django.views.generic import UpdateView
from django.urls import reverse_lazy




class ProgramaEstoque_updateView(UpdateView):
    model = ProgramacaoSaidaEstoque
    form_class = Program_saida_form
    template_name = 'controle_estoque/programa_estoque/program_cadastro.html'
    success_url =  reverse_lazy('controle_estoque:program_estoque_listaView')   


    def get_context_data(self, **kwargs):
        svg = '<svg class="bi" width="30" height="24" role="img" aria-label="Products"><use xlink:href="#grid"></use></svg>'
        context = super().get_context_data(**kwargs)
        context["svg"] = mark_safe(svg)
        context["title"] = 'Programação de Saída de Estoque'
        context ['active'] = 'program'
        context ['fornecedor'] = 'cadastro'
        return context
