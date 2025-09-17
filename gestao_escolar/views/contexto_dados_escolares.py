from rh.models import Escola, Decreto

def get_contexto_escola(ano, escola_id):
    """Retorna dicionário com dados da escola e seus cargos"""
    
    print (f'ano é :{ano}')

    local_destino = Escola.objects.get(id=escola_id)
    print (f'esco  é :{local_destino}')

    contexto = {
        "anoLetivo_id": ano,
        "escola": local_destino,
        "diretor": Decreto.objects.filter(
            destino=local_destino,
            profissao__nome_profissao="Diretor Escolar",
            Decreto_decretoAtivo__ano_ativo__id=ano
        ).last(),
        "vice_diretor": Decreto.objects.filter(
            destino=local_destino,
            profissao__nome_profissao="Vice-Diretor Escolar",
            Decreto_decretoAtivo__ano_ativo__id=ano
        ).last(),
        "coordenador": Decreto.objects.filter(
            destino=local_destino,
            profissao__nome_profissao="Coordenador Escolar",
            Decreto_decretoAtivo__ano_ativo__id=ano
        ).last(),
        "secretario": Decreto.objects.filter(
            destino=local_destino,
            profissao__nome_profissao="Secretária escolar",
            Decreto_decretoAtivo__ano_ativo__id=ano
        ).last(),
    }

    return contexto
