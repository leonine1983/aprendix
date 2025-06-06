from django import template

register = template.Library()

@register.filter(name='criar_sigla')
def criar_sigla(value):
    palavras = value.split()
    return ''.join(word[0].upper() for word in palavras)

@register.filter
def get_horario(horarios, dia, periodo):
    for horario in horarios:
        if horario.dia_semana == dia and horario.periodo == int(periodo):
            return horario
    return None

@register.filter()
def soma(val1, val2, val3):
    return val1 + val2 + val3

@register.filter
def unique_objects(queryset, field_name):
    """
    Retorna uma lista de objetos únicos de um queryset, 
    com base em um campo específico.

    Este filtro itera sobre um queryset e elimina objetos com valores repetidos 
    no campo especificado, retornando apenas a primeira ocorrência de cada valor único.

    Exemplo de uso no template:
        {% for item in queryset|unique_objects:"nome_campo" %}
            {{ item.nome }}
        {% endfor %}

    Args:
        queryset (iterable): Um queryset ou lista de objetos Django.
        field_name (str): O nome do campo que será usado para verificar duplicatas.

    Returns:
        list: Lista de objetos com valores únicos no campo especificado.
    """
    seen = set()
    unique_list = []
    for item in queryset:
        value = getattr(item, field_name)
        if value not in seen:
            seen.add(value)
            unique_list.append(item)
    return unique_list

@register.filter
def first_item(value):
    if isinstance(value, (list, tuple)) and value:
        return value[0]
    return None

@register.filter
def get_nota_por_trimestre(notas, trimestre):
    return next((n for n in notas if n.trimestre == trimestre), None)


@register.filter
def to(value):
    return range(1, value + 1)



@register.filter
def campo_conhecimento_count(disciplinas, campo):
    return sum(1 for d in disciplinas if d.campo_conhecimento == campo)

@register.filter
def make_tuple(a, b):
    return (a, b)

@register.filter
def get_historico(historico_list, disciplina_turma):
    disciplina, turma = disciplina_turma
    for h in historico_list:
        if h.grade.disciplina == disciplina and h.grade.turma.serie == turma:
            return h
    return None


@register.filter
def filter_campo_conhecimento(disciplinas, campo):
    return [d for d in disciplinas if d.campo_conhecimento == campo]

