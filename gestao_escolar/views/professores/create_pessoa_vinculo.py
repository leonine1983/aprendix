from rh.models import Vinculo_empregaticio, Pessoas
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .professor_form import Create_Pessoa_Vinculo_FORM


class Create_Pessoa_Vinculo(LoginRequiredMixin, CreateView):
    model = Vinculo_empregaticio
    #fields = '__all__'
    form_class = Create_Pessoa_Vinculo_FORM
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')    

    # Recebe o Id vindo pela url para inicializar o select no form
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs() 
        kwargs ['pessoa'] = Pessoas.objects.filter(pk = self.kwargs['pk'])        
        return kwargs
    
    def get_success_url(self) -> str:
        return reverse_lazy("Gestao_Escolar:Professores_Pessoa_aplica_vinculo_create", kwargs ={'pk':self.object.pessoa.id, 'vinculo':self.object.vinculo, 'ano':self.object.ano})
    
    def get_context_data(self, **kwargs):
        svg = '<i class="fs-6 fa-duotone fa-person-chalkboard"></i>'
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Professores | Criar Vínculo'          
        context['svg'] = svg 
        context['lista_all'] = Vinculo_empregaticio.objects.all()
        #context['now'] = datetime.now()     
        context['conteudo_page'] = "Professores-Pessoas-Vinculo"               
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional"        
        return context
            



            