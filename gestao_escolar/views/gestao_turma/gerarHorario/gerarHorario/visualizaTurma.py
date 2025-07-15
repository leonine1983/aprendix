from gestao_escolar.models import Horario, TurmaDisciplina, Periodo, DiaSemana
from django.shortcuts import render
from django.urls import reverse_lazy

from django import forms
from gestao_escolar.models import Horario

def visualizaHorarioTuram(request, turma_id):
    context = {
        'turmas_disciplinas': TurmaDisciplina.objects.filter(turma=turma_id),
        'horarios': Horario.objects.filter(turma=turma_id),
        'periodos': Periodo.objects.all(),
        'dias_semana': DiaSemana.objects.all(),
        'conteudo_page': "Gestão Turmas - GerarHorario"
         }

    return render(request, 'Escola/inicio.html', context)