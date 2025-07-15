from typing import Any
from django.forms import BaseModelForm
from django.http import HttpResponse
from django.views.generic import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from rh.models import Encaminhamentos, Escola, Contrato,Ano
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect


class EncaminhaEscola(LoginRequiredMixin, CreateView, SuccessMessageMixin):
    model = Encaminhamentos
    fields = ['profissao']
    success_message = "Profissional Encaminhado para a sua escola com sucesso, para o ano letivo atual!!"
    template_name = 'Escola/inicio.html'

    def get_form_kwargs(self):
        return super().get_form_kwargs()

    def form_valid(self, form: BaseModelForm):
        escola_id = self.request.session['escola_id']
        ano_letivo = self.request.session['anoLetivo_id']
        pk = self.kwargs['pk']
        
        # Pega a instancia do Contrato
        contrato_get = Contrato.objects.get(id=pk)
       
        # Verifica se a instancia é diferente do Ano Letivo atual
        if contrato_get.ano_contrato.id != ano_letivo:
            # Se for diferente, irá verificar se existe alguma instancia com o Ano Letivo atual
            if not Contrato.objects.filter(ano_contrato=ano_letivo, contratado = contrato_get.contratado.id).exists():                   
                print(f'o que tem no form segundo {Contrato.objects.filter(ano_contrato=ano_letivo)}')   
                novo_contrato = Contrato.objects.create(
                    ano_contrato=Ano.objects.get(id=ano_letivo),
                    contratado=contrato_get.contratado,
                    text_contrato=contrato_get.text_contrato,
                    nome_profissao=contrato_get.nome_profissao,
                    nome_escola=Escola.objects.get(id=escola_id),
                    salario=contrato_get.salario,
                    tempo_meses=contrato_get.tempo_meses
                )                
                novo_contrato.save()
               
                messages.success(self.request, f"Novo contrato para o {novo_contrato.contratado} para o ano de {novo_contrato.ano_contrato} criado com sucesso!!")

                escola = Escola.objects.get(id=escola_id)
                form.instance.encaminhamento = novo_contrato
                form.instance.destino = escola
                form.instance.profissao = contrato_get.nome_profissao  # Ajuste conforme necessário
                form.save()                
                return redirect(reverse('Gestao_Escolar:Professores_Pessoa_create'))
            else:
                user = Contrato.objects.get(ano_contrato=ano_letivo, contratado = contrato_get.contratado.id)
                print(f'O usuario {user}')
                escola = Escola.objects.get(id=escola_id)
                print(f'a escola {escola}')
                form.instance.encaminhamento = user      
                form.instance.destino = escola
                
                print(f'o que tem no form primero {user} esse é o dia do contato {contrato_get.contratado.id}')
                form.save()
            
            return redirect(reverse('Gestao_Escolar:Professores_Pessoa_create'))

        else:
            
            escola = Escola.objects.get(id=escola_id)
            contrato = Contrato.objects.get(id=pk, ano_contrato=ano_letivo)
            form.instance.encaminhamento = contrato           
            form.instance.destino = escola
            form.instance.profissao = contrato_get.nome_profissao  # Ajuste conforme necessário
            form.save()            
            return redirect(reverse('Gestao_Escolar:Professores_Pessoa_create'))

        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('Gestao_Escolar:Professores_Pessoa_create')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Professores | Encaminhamento para a Escola'          
        context['lista_all'] = Encaminhamentos.objects.filter(encaminhamento__contratado = self.kwargs['pk'])
        context['conteudo_page'] = "encaminha_para_escola"   
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional. "        
        return context   