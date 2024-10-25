from django.shortcuts import render
from gestao_escolar.models import *
from django.views.generic import ListView
from gestao_escolar.models import AnoLetivo
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy


class Seleciona_anoLetivo(LoginRequiredMixin, ListView):
    model = AnoLetivo
    template_name = 'Escola/inicio.html'
    context_object_name = 'anoLetivo'
        

    def get_context_data(self, **kwargs):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48"><path d="M38-160v-94q0-35 18-63.5t50-4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM9-103.5T622-423q69 8 130 23.5t99 35.5q33 19 52 47t19 63v94H738ZM358-481q-66 0-108-4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM94B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM90 108 4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM96-23 21t-9 31v34Zm260-321q39 0 64.5-25.5T448-631q0-39-25.5-64.5T358-721q-39 0-64.5 25.5T268-631q0 39 25.5 64.5T358-541Zm0 321Zm0-411Z"/></svg>'
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Selecione o ano letivo'          
        context['svg'] = svg 
        context['now'] = datetime.now()        
        context['conteudo_page'] = 'Ano Letivo'          
        
        context['page_ajuda'] = "<div class='m-2'>\
                                    <p>Oi! Precisa de ajuda <i class='fa-duotone fa-solid fa-message-question fs-2'></i></p>\
                                    <p>Oi! Vamos escolher um ano letivo.</p>\
                                    <p>Sempre que inicia o APRENDIX, é necessário além de escolher uma escola, deve selecionar o ano letivo<i class='fa-duotone fa-solid fa-hands-holding-heart'></i></p>\
                                    <p>Aqui nessa janela, lá no topo tem uma lista contendo todos os anos letivos disponíveis.</p>\
                                    <p>Basta você clicar lista, clicar no ano letivo e depois no botão SELECIONAR. Daí a mágica acontece</p>\
                                    <p>Vai lá e experimente. Qualquer coisa, estarei por aqui. Abraços...</p>\
                                </div>"
        
        return context