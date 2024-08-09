from rh.models import Pessoas, Encaminhamentos, Ano, Contrato
from gestao_escolar.models import AnoLetivo, Profissionais, Cargo
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from .create_defineProfissionais_FORM import Form_defineProfissionais


# DEFINE O CARGO QUE O PROFISSIONAL IRÁ EXERCER NA ESCOLA --------------------------------
class Create_Define_Profissional(LoginRequiredMixin, CreateView):
    model = Profissionais
    #fields = '__all__'
    form_class = Form_defineProfissionais
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')    

    def get_success_url(self):
        return reverse_lazy('Gestao_Escolar:Professores_Profissionais_create')    

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()  
        escola = self.request.session['escola_id']  
        profissionais_list = Profissionais.objects.values_list('nome__id', flat=True)
        encaminhamento_esc = Encaminhamentos.objects.filter(destino = escola, encaminhamento__ano_contrato = self.request.session['anoLetivo_id'] )
        kwargs['nome_query'] = encaminhamento_esc.exclude(id__in = profissionais_list )
        return kwargs
    
    def get_context_data(self, **kwargs):
        escola = self.request.session['escola_id']
        svg = '<i class="fs-6 fa-duotone fa-person-chalkboard"></i>'
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Professores'          
        context['svg'] = svg 

        
        context['lista_all'] = Profissionais.objects.filter(nome__destino = escola, nome__encaminhamento__ano_contrato = self.request.session['anoLetivo_id'] )       
        context['cargo_all'] = Cargo.objects.all()       
        context['conteudo_page'] = "cargos/funcionarios" 
        context['page_ajuda'] = "<h3>Definir cargo para o funcionário</h3>\
                <hr>\
                <h4 >Para otimizar a gestão escolar e aprimorar o controle dos colaboradores,\
                   é essencial categorizar cada profissional vinculado à instituição em uma classificação\
                    específica. Esta categorização influenciará o processo de alocação dos professores nas\
                     turmas e facilitará a geração de relatórios por categoria ou cargo.</h4>"        
        return context       
            