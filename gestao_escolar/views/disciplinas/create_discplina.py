from typing import Any
from django.db import models
from gestao_escolar.models import Disciplina
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime
from django.urls import reverse_lazy
from .disciplina_form import Diciplina_form
from django.db.models import Q

class Create_disciplinas(LoginRequiredMixin, CreateView):
    model = Disciplina
    # fields = ['nome']
    form_class = Diciplina_form
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')

    def get_queryset(self):
        disciplinas = self.request.GET.get('busca-disciplina')
        if disciplinas:
            busca_disciplina = Disciplina.objects.filter(Q(nome__icontains = disciplinas))
        else:
            busca_disciplina = Disciplina.objects.all()
        return busca_disciplina    
    
    def get_context_data(self, **kwargs):        
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Disciplinas'
        context['conteudo_page'] = 'Criar Disciplina' 
        context['query'] = self.get_queryset()
        
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
            



            