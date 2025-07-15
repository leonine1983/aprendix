# views.py
import requests
from django.http import JsonResponse
from gestao_escolar.models import Bairro, Cidade

def carregar_cidades(request):
    uf_id = request.GET.get('uf')
    if uf_id:
        response = requests.get(f'https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf_id}/municipios')
        if response.status_code == 200:
            cidades = response.json()
            cidades_formatadas = [{'id': c['id'], 'nome': c['nome']} for c in cidades]
            return JsonResponse({'cidades': cidades_formatadas})
    return JsonResponse({'cidades': []})


def carregar_bairros(request):
    cidade_id = request.GET.get('cidade')
    bairros = Bairro.objects.filter(cidade_id=cidade_id).values('id', 'nome')
    return JsonResponse({'bairros': list(bairros)})
