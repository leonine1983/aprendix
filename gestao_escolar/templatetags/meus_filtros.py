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