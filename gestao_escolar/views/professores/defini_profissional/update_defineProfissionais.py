from rh.models import Pessoas, Encaminhamentos
from gestao_escolar.models import Profissionais, Cargo
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from .create_defineProfissionais_FORM import Form_defineProfissionais_update

# ATUALIZA O CARGO QUE O PROFISSIONAL IRÁ EXERCER NA ESCOLA --------------------------------
class Update_Define_Profissional(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Profissionais
    form_class = Form_defineProfissionais_update
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')    

    def get_success_url(self):
        return reverse_lazy('Gestao_Escolar:Professores_Profissionais_create')   
    
    def get_context_data(self, **kwargs):
        escola = self.request.session['escola_id']
        svg = '<i class="fs-6 fa-duotone fa-person-chalkboard"></i>'
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Professores'          
        context['svg'] = svg 

        
        context['lista_all'] = Profissionais.objects.filter(nome__destino = escola, nome__encaminhamento__ano_contrato__anoletivo = self.request.session['anoLetivo_id'] )       
        context['cargo_all'] = Cargo.objects.all()       
        context['conteudo_page'] = "cargos/funcionarios" 
        context['active'] = 'active'
        context['page_ajuda'] = "<h3>Definir cargo para o funcionário</h3>\
                <hr>\
                <h4 >Para otimizar a gestão escolar e aprimorar o controle dos colaboradores,\
                   é essencial categorizar cada profissional vinculado à instituição em uma classificação\
                    específica. Esta categorização influenciará o processo de alocação dos professores nas\
                     turmas e facilitará a geração de relatórios por categoria ou cargo.</h4>"        
        return context       
            