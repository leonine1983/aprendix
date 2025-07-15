from rh.models import Ano
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import DeleteView
from .forms import Ano_form
from django.urls import reverse_lazy


class Ano_deleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Ano
    #fields = '__all__'
    template_name = 'rh/inicio.html'
    success_url = reverse_lazy('RH:Ano_deleteView')
    success_message = 'Profissão excluída com sucesso!!'

    def get_context_data(self, **kwargs):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 448 512"><!--! Font Awesome Free 6.4.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M96 32V64H48C21.5 64 0 85.5 0 112v48H448V112c0-26.5-21.5-48-48-48H352V32c0-17.7-14.3-32-32-32s-32 14.3-32 32V64H160V32c0-17.7-14.3-32-32-32S96 14.3 96 32zM448 192H0V464c0 26.5 21.5 48 48 48H400c26.5 0 48-21.5 48-48V192z"/></svg>'
        nome_instacia = self.get_object()
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Ano'          
        context['svg'] = svg 
        context['conteudo_page'] = 'Deleta Ano'        
        context['nome_instancia'] = nome_instacia.ano 
        context['lista_ano'] = Ano.objects.all()



        return context