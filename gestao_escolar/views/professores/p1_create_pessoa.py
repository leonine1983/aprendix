from rh.models import Pessoas, Encaminhamentos, Ano, Contrato
from gestao_escolar.models import  Profissionais
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .professor_form import Pessoa_form
from rh.models import Config_plataforma


class Create_Pessoa_Professores(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Pessoas
    form_class = Pessoa_form
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')    
    success_message = 'Pessoa registrada com sucesso'    

    def get_success_url(self):
        return reverse_lazy('Gestao_Escolar:Professores_Pessoa_vinculo_create', kwargs ={'pk':self.object.id})
    
    def get_context_data(self, **kwargs):
        svg = '<i class="fs-6 fa-duotone fa-person-chalkboard"></i>'
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Professores'          
        context['svg'] = svg 
        #ano = 
        #  context['lista_all'] = Encaminhamentos.objects.filter(encaminhamento__ano_decreto = request.session['anoLetivo_id'])
        escola = self.request.session['escola_id']
        context['lista_all'] = Encaminhamentos.objects.filter(destino = escola, encaminhamento__ano_contrato__anoletivo = self.request.session['anoLetivo_id'] )

        contratos_condicoes_contrato = Contrato.objects.filter(
                                                                    nome_escola=escola,
                                                                    ano_contrato__anoletivo=self.request.session['anoLetivo_id']
                                                                )

                                                                # Passo 2: Excluir contratos que atendem às condições do modelo Encaminhamentos
        lista_all_pessoas = contratos_condicoes_contrato.exclude(
                                                                    encaminhamento_escolar__destino=escola
                                                                )

        context['lista_all_pessoas'] = lista_all_pessoas
        context['lista_all_escola'] = Profissionais.objects.filter(nome__destino = escola, nome__encaminhamento__ano_contrato__anoletivo = self.request.session['anoLetivo_id'] )
        contratados_anoLetivo = Contrato.objects.values_list('id', flat=True)
        context['lista_pessoas'] = Pessoas.objects.exclude(pessoa_contratada__id__in= contratados_anoLetivo)

        # Realize a consulta para obter informações do Contrato com base nas condições e exclua aqueles que atendem às condições de Encaminhamentos 
        if Config_plataforma.objects.exists():
            config = Config_plataforma.objects.first()
            if config.rh_Ativo:
                context['rh_ativo'] = "True"
            else:
                context['rh_ativo'] = "False"            

        #context['now'] = datetime.now()     
        context['conteudo_page'] = "Professores-Pessoas"               
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."        
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if not self.object:
            messages.error(self.request, 'Não foi possível criar o registro.')
        else:
            messages.success(self.request, 'Criado com sucesso.')
        return response
        



            