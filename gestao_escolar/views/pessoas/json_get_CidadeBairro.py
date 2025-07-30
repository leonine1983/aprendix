from django.http import JsonResponse
from rh.models import Cidade, Bairro

def get_cidades(request):
    estado_id = request.GET.get('estado_id')
    cidades = list(Cidade.objects.filter(estado_id=estado_id).values('id', 'nome'))
    return JsonResponse({'cidades': cidades})


def get_bairros(request):
    cidade_id = request.GET.get('cidade_id')
    bairros = list(Bairro.objects.filter(cidade_id=cidade_id).values('id', 'nome'))
    return JsonResponse({'bairros': bairros})

