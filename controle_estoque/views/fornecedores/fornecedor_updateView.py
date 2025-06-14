from controle_estoque.models import Fornecedor
from controle_estoque.form import FornecedorForm
from django.utils.safestring import mark_safe
from django.views.generic import UpdateView
from django.urls import reverse_lazy




class Fornecedor_updateView(UpdateView):
    model = Fornecedor
    fields = ['nome', 'endereco', 'telefone', 'cnpj','email']
    template_name = 'controle_estoque/fornecedores/fornecedores_cadastro.html'
    success_url =  reverse_lazy('controle_estoque:fornecedor_listaView')

    def get_context_data(self, **kwargs):
        svg = '<svg class="bi" width="30"  xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512"><!--! Font Awesome Pro 6.4.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M256 48c0-26.5 21.5-48 48-48H592c26.5 0 48 21.5 48 48V464c0 26.5-21.5 48-48 48H381.3c1.8-5 2.7-10.4 2.7-16V253.3c18.6-6.6 32-24.4 32-45.3V176c0-26.5-21.5-48-48-48H256V48zM571.3 347.3c6.2-6.2 6.2-16.4 0-22.6l-64-64c-6.2-6.2-16.4-6.2-22.6 0l-64 64c-6.2 6.2-6.2 16.4 0 22.6s16.4 6.2 22.6 0L480 310.6V432c0 8.8 7.2 16 16 16s16-7.2 16-16V310.6l36.7 36.7c6.2 6.2 16.4 6.2 22.6 0zM0 176c0-8.8 7.2-16 16-16H368c8.8 0 16 7.2 16 16v32c0 8.8-7.2 16-16 16H16c-8.8 0-16-7.2-16-16V176zm352 80V480c0 17.7-14.3 32-32 32H64c-17.7 0-32-14.3-32-32V256H352zM144 320c-8.8 0-16 7.2-16 16s7.2 16 16 16h96c8.8 0 16-7.2 16-16s-7.2-16-16-16H144z"/></svg>'
        context = super().get_context_data(**kwargs)
        context["svg"] = mark_safe(svg)
        context ['active'] = 'fornecedor'
        context ['title'] = 'Atualizar dados do Fornecedor'
        context ['fornecedor'] = 'cadastro'
        context ['update'] = 'update'
        return context