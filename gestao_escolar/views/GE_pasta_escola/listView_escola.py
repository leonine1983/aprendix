from rh.models import Escola
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime


class ListView_Escola(LoginRequiredMixin, ListView):
    model = Escola
    template_name = 'Escola/inicio.html'
    context_object_name = 'escolas'

    def get_context_data(self, **kwargs):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48"><path d="M38-160v-94q0-35 18-63.5t50-4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM9-103.5T622-423q69 8 130 23.5t99 35.5q33 19 52 47t19 63v94H738ZM358-481q-66 0-108-4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM94B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM90 108 4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM96-23 21t-9 31v34Zm260-321q39 0 64.5-25.5T448-631q0-39-25.5-64.5T358-721q-39 0-64.5 25.5T268-631q0 39 25.5 64.5T358-541Zm0 321Zm0-411Z"/></svg>'
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Selecione uma escola'          
        context['svg'] = svg 
        context['now'] = datetime.now()
        
        context['conteudo_page'] = 'Nome das Escolas'       
        
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional. </b>\
            <hr>\
                <div class='border bg-secondary p-2'>\
                    <h2>Pessoar a ser contratada</h2>\
                    <p>Espaço onde é selecionado no nome da pessoa que será contratada. Se por alguma razão estiver vazio, clique aqui: <a class='btn btn-sm btn-primary' href='pessoas/create/'>Clique aqui para cadastrar uma pessoa no sistema</a></p>\
                </div>\
                <div class=' p-2'>\
                    <p><h2>Ano de contrato</h2>\
                    <p>Espaço onde é selecionado o ano em que o profissional será contratado. Se por alguma razão estiver vazio, clique aqui: <a class='btn btn-sm btn-secondary' href='ano/create/'>Clique aqui para cadastrar um ANO no sistema</a></p>\
                </div>\
                <div class='border bg-secondary p-2'>\
                    <p><h2>Tipo de contrato</h2>\
                    <p>Espaço onde é selecionado o modelo de contrato que será utilizado para a contratação. Se estiver vazio,  clique aqui: <a class='btn btn-sm btn-primary' href='ano/create/'>Clique aqui para criar um MODELO DE CONTRATO no sistema</a></p>\
                </div>\
                <div class=' p-2'>\
                    <p><h2>Função que irá desempenhar na escola</h2>\
                    <p>Local em que é definido a função pela qual o profissional está sendo contratado</p>\
                </div>\
                <div class='border bg-secondary p-2'>\
                    <p><h2>Escola onde o profissional irá desempenhar suas funções</h2>\
                    <p>Espaço onde é selecionado a instituição que o profissional desempenhará suas funções. Se estiver vazio,  clique aqui: <a class='btn btn-sm btn-primary' href='escola/create/'>Clique aqui para Adicionar uma Escola</a></p>\
                </div>"
        
        return context
            



            