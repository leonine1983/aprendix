from gestao_escolar.models import *
from django.shortcuts import redirect
from django.urls import reverse
from gestao_escolar.models import AnoLetivo
from rh.models import Escola, Decreto
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import plotly.express as px
import plotly.io as pio
from gestao_escolar.utils import processar_dados


@login_required
def seleciona_anoLetivo_session(request, pk):
    ano = AnoLetivo.objects.get(id=pk)  # Obtendo o objeto AnoLetivo pelo ID
    if ano:
        processar_dados(request, ano, request.session['escola_id'])    
    ano = request.session.get('anoLetivo_nome', 'Ano letivo não definido')
    messages.success(request, f"Ano letivo selecionado: {ano}")
    
    return redirect(reverse('Gestao_Escolar:GE_Escola_inicio'))
