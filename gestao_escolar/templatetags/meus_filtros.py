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

