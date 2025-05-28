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
    anol = request.session.get('anoLetivo_nome', 'Ano letivo não definido')
    messages.success(request, f"Ano letivo selecionado: {anol}")



    # Busca dados de alunos destros ou canhotos
    lateralidade_data = []

    turmas = Turmas.objects.filter(escola=request.session['escola_id'], ano_letivo=ano)

    for turma in turmas:
        matriculas = Matriculas.objects.filter(turma=turma)
        alunos = Alunos.objects.filter(related_matricula_alunos__in=matriculas)

        destros = alunos.filter(lateralidade='destro').count()
        canhotos = alunos.filter(lateralidade='canhoto').count()
        ambidestros = alunos.filter(lateralidade='ambidestro').count()

        lateralidade_data.append({
            'nome': turma.nome,
            'descritivo': turma.descritivo_turma,
            'destros': destros,
            'canhotos': canhotos,
            'ambidestros': ambidestros,
        })

    # Totais gerais
    total_destros = sum(item['destros'] for item in lateralidade_data)
    total_canhotos = sum(item['canhotos'] for item in lateralidade_data)
    total_ambidestros = sum(item['ambidestros'] for item in lateralidade_data)

    request.session['turma_lateralidade'] = lateralidade_data
    request.session['totais_lateralidade'] = {
        'destros': total_destros,
        'canhotos': total_canhotos,
        'ambidestros': total_ambidestros
    }

    
    return redirect(reverse('Gestao_Escolar:GE_Escola_inicio'))
