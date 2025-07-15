from django.forms.models import BaseModelForm
from django.http import HttpResponse
from rh.models import Vinculo_empregaticio, Pessoas, Encaminhamentos, Contrato, Profissao
from rh.models import Escola
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .professor_form import Create_Pessoa_Encaminhamento_form
from django.http import HttpResponseRedirect

 
class Create_Pessoa_Encaminhamento(LoginRequiredMixin, CreateView):
    model = Encaminhamentos
    # fields = '__all__'
    form_class = Create_Pessoa_Encaminhamento_form
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')    

    # Recebe o Id vindo pela url para inicializar o select no form
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs() 
        kwargs['encaminhamento'] = Contrato.objects.filter(pk=self.kwargs['pk'])  
        kwargs['destino'] = Escola.objects.filter(pk=self.kwargs['destino'])
        kwargs['profissao'] = Profissao.objects.filter(pk=self.kwargs['profissao'])       

        # Verifica se os filtros retornaram resultados
        if not kwargs['encaminhamento']:
            kwargs['encaminhamento'] = Contrato.objects.none()
        if not kwargs['destino']:
            kwargs['destino'] = Escola.objects.none()
        if not kwargs['profissao']:
            kwargs['profissao'] = Profissao.objects.none()
        return kwargs  
    
    # Salva automaticamente os dado se o form for válido
    def form_valid(self, form) :
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())      

     
            