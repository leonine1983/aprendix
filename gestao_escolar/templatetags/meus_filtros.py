from django import template

register = template.Library()

@register.filter(name='criar_sigla')
def criar_sigla(value):
    # Dividir o valor em palavras
    palavras = value.split()

    # Pegar a primeira letra de cada palavra e juntá-las
    sigla = ''.join(word[0].upper() for word in palavras)

    return sigla


@register.filter
def get_horario(horarios, dia, periodo):
    for horario in horarios:
        if horario.dia_semana == dia and horario.periodo == int(periodo):
            return horario
    return None



# Realiza cálculos de adição no template
@register.filter()
def soma(val1, val2, val3):
    return val1+val2+val3


""""""
@register.filter
def unique_objects(queryset, field_name):
    """
    Retorna uma lista de objetos únicos com base em um campo específico de um queryset.

    Args:
        queryset: Um queryset de objetos que contém o campo a ser verificado.
        field_name: O nome do campo cujo valor será filtrado para ser único.

    Returns:
        Uma lista contendo apenas objetos únicos do campo especificado.

    """
    seen = set()  # Conjunto para rastrear valores já vistos
    unique_list = []  # Lista para armazenar objetos únicos
    for item in queryset:
        value = getattr(item, field_name)  # Obtém o valor do campo
        if value not in seen:  # Verifica se o valor já foi visto
            seen.add(value)  # Adiciona o valor ao conjunto de vistos
            unique_list.append(item)  # Adiciona o objeto à lista única
    return unique_list  # Retorna a lista de objetos únicos


@register.filter
def first_item(value):
    if isinstance(value, (list, tuple)) and value:
        return value[0]
    return None

"""
exemplo de como usar os filtros first_item() e unique_objects()
 
                                            {% with primeiro_recu=aluno.gestao_turmas_related.all|unique_objects:'recuperacao_final'|first_item %}
                                            {{primeiro_recu.recuperacao_final}}d {{aluno.gestao_turmas_related.first.recuperacao_final}}
                                            {{primeiro_recu.aprovado_recupera}}
                                                {% if primeiro_recu.recuperacao_final is not None %}
                                                    {% if primeiro_recu.recuperacao_final > 5 %}
                                                        Aprovado na recuperação
                                                    {% else %}
                                                        Reprovado na recuperação
                                                    {% endif %}
                                                {% endif %}
                                            {% endwith %}

"""