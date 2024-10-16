from rh.models import Ano, Escola
from gestao_escolar.models import Turmas
from django.shortcuts import render

def boletim(request):
    ano = Ano.objects.get(id = request.session['anoLetivo_id'])
    escola = Escola.objects.get(id = request.session['escola_id'])
    turmas_boletim = Turmas.objects.filter(escola = escola, ano_letivo = ano)

    context = {
        'conteudo_page':"boletim",
        'turma' : turmas_boletim
    }
    return render(request, 'Escola/inicio.html', context)


