from gestao_escolar.models import Matriculas, Turmas, Remanejamento
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime
from django.urls import reverse_lazy
from .remanejamento_form import Matricula_form
from django.core.paginator import Paginator


class Create_Remanejamento(LoginRequiredMixin, CreateView):
    model = Remanejamento
    #fields = '__all__'
    form_class = Matricula_form
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')    


    

    
    def get_context_data(self, **kwargs):
        svg = '<i class="fa-sharp fa-regular fa-layer-plus"></i>'
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Remanejamento'          
        context['svg'] = svg 

        context['pk_aluno'] = self.kwargs['pk']
        context['info_matrilula'] = Matriculas.objects.filter(pk = self.kwargs['pk'])
        #context['now'] = datetime.now()     
        context['conteudo_page'] = "Remaneja Aluno"       
        
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
            



            