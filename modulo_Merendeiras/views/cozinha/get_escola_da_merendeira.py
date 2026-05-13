"""
modulo_merendeiras/utils.py

Funções utilitárias compartilhadas entre as views do módulo.
"""

from rh.models import Escola


def get_escola_da_merendeira(user):
    """
    Retorna a Escola associada ao usuário logado (merendeira/gestor).

    Adapte o acesso conforme o modelo do seu projeto.
    Exemplos comuns:
        - user.perfil.escola
        - user.funcionario.escola
        - Escola.objects.filter(usuarios=user).first()
    """
    if hasattr(user, 'perfil') and hasattr(user.perfil, 'escola'):
        return user.perfil.escola

    if hasattr(user, 'funcionario') and hasattr(user.funcionario, 'escola'):
        return user.funcionario.escola

    # Fallback de desenvolvimento — remova em produção
    return Escola.objects.first()