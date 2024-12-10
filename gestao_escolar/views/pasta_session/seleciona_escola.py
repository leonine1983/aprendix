
from gestao_escolar.models import *
from django.shortcuts import  redirect
from django.urls import reverse
from rh.models import Escola, Prefeitura
from admin_acessos.models import NomeclaturaJanelas
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib import messages

# Essa view lida com a seleção da escola e armazena os dados na sessão
@login_required
def Seleciona_escola(request, pk):
    # Recupera a escola com base no id fornecido
    escola = Escola.objects.get(pk = pk)
    nomeclatura = NomeclaturaJanelas.objects.latest('id')
    prefeitura = Prefeitura.objects.get(pk = 1)    
    
    # outros
    matriculas_painel = Turmas.objects.filter(escola = escola)
    # Armazena o Id e o nome da escola na sessão
    request.session['escola_id'] = escola.id
    request.session['escola_nome'] = escola.nome_escola
    request.session['escola_nome_query'] = escola
    request.session['prefeitura'] = prefeitura
    request.session['nomeclatura'] = nomeclatura
    request.session['matriculas_painel'] = matriculas_painel
    request.session['dia'] = datetime.now().day    
    meses = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    # Obtém o mês atual (número de 1 a 12) e armazena o nome correspondente na sessão
    mes_atual = datetime.now().month
    request.session['mes'] = meses[mes_atual - 1]
    
    # Redireciona a pagina
    messages.success(request, "Escola selecionada com sucesso!")
    return redirect(reverse('Gestao_Escolar:GE_anoLetivo'))