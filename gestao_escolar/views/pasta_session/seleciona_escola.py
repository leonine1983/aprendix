
from gestao_escolar.models import *
from django.shortcuts import  redirect
from django.urls import reverse
from rh.models import Escola
from admin_acessos.models import NomeclaturaJanelas
from django.contrib.auth.decorators import login_required

# Essa view lida com a seleção da escola e armazena os dados na sessão
@login_required
def Seleciona_escola(request, pk):
    # Recupera a escola com base no id fornecido
    escola = Escola.objects.get(pk = pk)
    nomeclatura = NomeclaturaJanelas.objects.latest('id')
    # Armazena o Id e o nome da escola na sessão
    request.session['escola_id'] = escola.id
    request.session['escola_nome'] = escola.nome_escola
    request.session['nomeclatura'] = nomeclatura
    # Redireciona a pagina
    return redirect(reverse('Gestao_Escolar:GE_anoLetivo'))