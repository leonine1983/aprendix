from rh.models import Contrato, Pessoas
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import DetailView
from ..pasta_contrato_texto.forms import Texto_contrato_form
from django.urls import reverse_lazy
import re
from django.utils.safestring import mark_safe
from django.shortcuts import render
from django.contrib.humanize.templatetags.humanize import naturaltime
from datetime import date


from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import DetailView
from ..pasta_contrato_texto.forms import Texto_contrato_form
from django.urls import reverse_lazy
import re
from django.utils.safestring import mark_safe

from django.shortcuts import render

class Contrato_detailView(DetailView):
    model = Contrato
    template_name = 'rh/inicio.html'
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)       
        contrato = Contrato.objects.get(id=self.kwargs['pk']) 
        svg = '<svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 576 512">...</svg>'
        context["svg"] = svg
        context["titulo_page"] = 'Contrato de Trabalho'
        context["conteudo_page"] = f"Contrato do funcionário {contrato.contratado}"    
        
        contrato = Contrato.objects.filter(id=self.kwargs['pk'])     
        for contratos in contrato:
            context["conteudo"] = mark_safe(contratos.text_contrato.texto)
            
            tempo_meses_str = str(contratos.tempo_meses)
            data_inicio_contrato_str = str(contratos.data_inicio_contrato)
            data_fim_contrato_str = str(contratos.data_fim_contrato)   
            salario_str = str(contratos.salario)
            nome_str = str(contratos.contratado)
            data_nascimento_str = str(contratos.contratado.data_nascimento)            
            idade_str = str(contratos.contratado.idade)
            cpf_str = str(contratos.contratado.cpf)
            rg_str = str(contratos.contratado.rg)            
            rua_str = str(contratos.contratado.rua) 
            complemento_str = str(contratos.contratado.complemento) 
            numero_casa_str = str(contratos.contratado.numero_casa)                         
            bairro_str = str(contratos.contratado.bairro)
            cidade_str = str(contratos.contratado.cidade)
            cep_str = str(contratos.contratado.cep)
            local_str = str(contratos.nome_escola)
            nome_profissao_str = str(contratos.nome_profissao)

            context["conteudo"] = mark_safe(context["conteudo"].replace("{{tempo_meses}}", tempo_meses_str)) 
            context["conteudo"] = mark_safe(context["conteudo"].replace("{{data_inicio_contrato}}", data_inicio_contrato_str)) 
            context["conteudo"] = mark_safe(context["conteudo"].replace("{{data_fim_contrato}}", data_fim_contrato_str))  
            context["conteudo"] = mark_safe(context["conteudo"].replace("{{object.salario}}", salario_str))  
            context["conteudo"] = mark_safe(context["conteudo"].replace("{{nome}}", nome_str))                     
            context["conteudo"] = mark_safe(context["conteudo"].replace("{{data_nascimento}}", data_nascimento_str)) 
            context["conteudo"] = mark_safe(context["conteudo"].replace("{{idade}}", idade_str)) 
            context["conteudo"] = mark_safe(context["conteudo"].replace("{{cpf}}", cpf_str))
            context["conteudo"] = mark_safe(context["conteudo"].replace("{{rg}}", rg_str))   
            context["conteudo"] = mark_safe(context["conteudo"].replace("{{rua}}", rua_str))            
            context["conteudo"] = mark_safe(context["conteudo"].replace("{{complemento}}", complemento_str))             
            context["conteudo"] = mark_safe(context["conteudo"].replace("{{complemento}}", numero_casa_str)) 
            context["conteudo"] = mark_safe(context["conteudo"].replace("{{bairro}}", bairro_str)) 
            context["conteudo"] = mark_safe(context["conteudo"].replace("{{cidade}}", cidade_str))        
            context["conteudo"] = mark_safe(context["conteudo"].replace("{{cep}}", cep_str))             
            context["conteudo"] = mark_safe(context["conteudo"].replace("{{local}}", local_str))
            context["conteudo"] = mark_safe(context["conteudo"].replace("{{nome_profissao}}", nome_profissao_str))    

            context["tempo_meses"] = f'{tempo_meses_str} meses'
            context["data_inicio_contrato"] = date.fromisoformat(data_inicio_contrato_str)
            context["data_fim_contrato"] = date.fromisoformat(data_fim_contrato_str) 
            context["data_nascimento"] = date.fromisoformat(data_nascimento_str)
            context["idade"] = idade_str
            context["cpf"] = cpf_str
            context["rg"] = rg_str
            context["rua"] = rua_str
            context["complemento"] = complemento_str
            context["numero_casa"] = numero_casa_str
            context["bairro"] = bairro_str
            context["cidade"] = cidade_str
            context["cep"] = cep_str
            context["nome"] = contratos.contratado
            context["local"] = local_str
            context["nome_profissao"] = nome_profissao_str 

        return context
