from django.shortcuts import render
from django.http import request
from controle_estoque.models import Fornecedor, Alimentos, Movimentacao_Estoque, Categoria_alimentos
from django.db.models import Count

# Create your views here.
def index (request):
    data = 'index'
    quant = len(Fornecedor.objects.all())
    alimentos_estoque = Alimentos.objects.all()
    alimmentos_quant = len(Alimentos.objects.all())    
    categoria = Categoria_alimentos.objects.all()  
    
    movimenta_estoque = Movimentacao_Estoque.objects.all()[:4]
    return render (request, 'Controle_Estoque/index.html', {
        'active': data,
        'categoria': categoria,
        'quant_fornecedores' : quant,
        'alimentos' : alimentos_estoque,
        'alimentos_total' : alimmentos_quant,
        'movimenta_estoque' : movimenta_estoque
        })


"""
paciente_dia = envio_triagem.objects.filter(triagem_concluida = 1) & envio_triagem.objects.filter(data_triagem_concluida = data)  
pacient_localidade = paciente_dia.values('paciente_envio_triagem__bairro__bairro_nome').annotate(Total = Count('paciente_envio_triagem__bairro') )

"""