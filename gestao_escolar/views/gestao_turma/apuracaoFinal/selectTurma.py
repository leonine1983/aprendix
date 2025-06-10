from gestao_escolar.models import Turmas, Matriculas
from django.shortcuts import get_object_or_404, render



def listaTurmaApuracao (request):
    escola = request.session['escola_id']
    ano = request.session['anoLetivo_id']
    turma = Turmas.objects.filter(escola__id = escola, ano_letivo__id = ano)

    return render(request,'Escola/inicio.html' ,{
        'turma': turma,
        'conteudo_page': 'SelecinaTurmaApuração',
        'title_page': 'APURAÇÃO FINAL: Selecione um turma'
    })



def selecionaTurmaSelecionada (request, turma_id):
    escola = request.session['escola_id']
    turma = Matriculas.objects.filter(turma__id = turma_id)

    return render(request,'Escola/inicio.html' ,{
        'turma': turma,
        'conteudo_page': 'ApuraçãoFinal',
        'title_page': f'APURAÇÃO FINAL: {turma}'
    })