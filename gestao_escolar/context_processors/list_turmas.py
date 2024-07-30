from gestao_escolar.models import Turmas
from django.contrib.auth import authenticate

def list_turmas (request):
    contexto = {}
    if not authenticate:
        ano = request.session['anoLetivo_id']    
        escola =  request.session['escola_id']
        contexto ['turmas'] = Turmas.objects.filter(escola = escola, ano_letivo = ano)
    else:
         contexto ['turmas'] = Turmas.objects.all()

    return contexto