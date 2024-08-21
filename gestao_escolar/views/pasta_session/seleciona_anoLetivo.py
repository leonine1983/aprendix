from gestao_escolar.models import *
from django.shortcuts import redirect
from django.urls import reverse
from gestao_escolar.models import AnoLetivo
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def seleciona_anoLetivo_session(request, pk):
    ano = AnoLetivo.objects.get(id=pk)  # Obtendo o objeto AnoLetivo pelo ID
    print(f'ano é {ano}')
    if ano:
        request.session['anoLetivo_id'] = ano.id    
        request.session['anoLetivo_nome'] = str(ano.ano) 

    
    ano = request.session.get('anoLetivo_nome', 'Ano letivo não definido')
    messages.success(request, f"Ano letivo selecionado: {ano}")


    return redirect(reverse('Gestao_Escolar:GE_Escola_inicio'))
