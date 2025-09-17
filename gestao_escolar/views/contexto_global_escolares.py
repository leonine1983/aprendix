from rh.models import Escola, Decreto

def get_contexto_escola(ano, escola_id):
    """Retorna dicionário com dados da escola e seus cargos"""
    local_destino = Escola.objects.get(id=escola_id)

    contexto = {
        "anoLetivo_id": ano.id,
        "escola": local_destino,
        "diretor": Decreto.objects.filter(
            destino=local_destino,
            profissao__nome_profissao="Diretor Escolar",
            Decreto_decretoAtivo__ano_ativo__id=ano.id
        ).last(),
        "vice_diretor": Decreto.objects.filter(
            destino=local_destino,
            profissao__nome_profissao="Vice-Diretor Escolar",
            Decreto_decretoAtivo__ano_ativo__id=ano.id
        ).last(),
        "coordenador": Decreto.objects.filter(
            destino=local_destino,
            profissao__nome_profissao="Coordenador Escolar",
            Decreto_decretoAtivo__ano_ativo__id=ano.id
        ).last(),
        "secretario": Decreto.objects.filter(
            destino=local_destino,
            profissao__nome_profissao="Secretária escolar",
            Decreto_decretoAtivo__ano_ativo__id=ano.id
        ).last(),
    }

    return contexto
