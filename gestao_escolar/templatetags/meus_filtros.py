from django import template

register = template.Library()

@register.filter(name='criar_sigla')
def criar_sigla(value):
    """
    Cria uma sigla a partir de uma string de palavras.

    Exemplo:
        {{ "Ensino Fundamental" | criar_sigla }}
        Resultado: "EF"
    """
    palavras = value.split()
    return ''.join(word[0].upper() for word in palavras)


@register.filter
def get_horario(horarios, dia, periodo):
    """
    Retorna o horário correspondente ao dia e período informados.

    Exemplo:
        {{ horarios|get_horario:2:1 }} → Segunda-feira, primeiro período
    """
    for horario in horarios:
        if horario.dia_semana == dia and horario.periodo == int(periodo):
            return horario
    return None


@register.filter
def soma(val1, val2, val3):
    """
    Soma três valores numéricos.

    Exemplo:
        {{ 2|soma:3:4 }} → 9
    """
    return val1 + val2 + val3


@register.filter
def unique_objects(queryset, field_name):
    """
    Retorna objetos únicos de um queryset com base em um campo.

    Exemplo:
        {% for item in lista|unique_objects:"disciplina" %}
            {{ item.disciplina.nome }}
        {% endfor %}
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
    """
    Retorna o primeiro item de uma lista ou tupla.

    Exemplo:
        {{ lista|first_item }}
    """
    if isinstance(value, (list, tuple)) and value:
        return value[0]
    return None


@register.filter
def get_nota_por_trimestre(notas, trimestre):
    """
    Retorna o objeto de nota correspondente ao trimestre.

    Exemplo:
        {{ aluno.notas|get_nota_por_trimestre:trimestre_atual }}
    """
    return next((n for n in notas if n.trimestre == trimestre), None)


@register.filter
def to(value):
    """
    Gera uma sequência de 1 até o valor passado (inclusive).

    Exemplo:
        {% for i in 5|to %} {{ i }} {% endfor %}
        → 1 2 3 4 5
    """
    return range(1, value + 1)


@register.filter
def campo_conhecimento_count(disciplinas, campo):
    """
    Conta quantas disciplinas pertencem ao campo de conhecimento dado.

    Exemplo:
        {{ disciplinas|campo_conhecimento_count:"linguagens" }}
    """
    return sum(1 for d in disciplinas if d.campo_conhecimento == campo)


@register.filter
def make_tuple(a, b):
    """
    Retorna uma tupla com dois valores.

    Exemplo:
        {% with par=valor1|make_tuple:valor2 %}
            {{ par.0 }} e {{ par.1 }}
        {% endwith %}
    """
    return (a, b)


@register.filter
def get_historico(historico_list, disciplina_turma):
    """
    Busca um item da lista de históricos com base na disciplina e série da turma.

    Exemplo:
        {{ historicos|get_historico:disciplina|make_tuple:turma.serie }}
    """
    disciplina, turma = disciplina_turma
    for h in historico_list:
        if h.grade.disciplina == disciplina and h.grade.turma.serie == turma:
            return h
    return None


@register.filter
def filter_campo_conhecimento(disciplinas, campo):
    """
    Filtra disciplinas por campo de conhecimento.

    Exemplo:
        {% for d in disciplinas|filter_campo_conhecimento:"matematica" %}
            {{ d.nome }}
        {% endfor %}
    """
    return [d for d in disciplinas if d.campo_conhecimento == campo]


@register.filter
def filter_tipo_disciplina(disciplinas, tipo):
    """
    Filtra disciplinas por tipo de disciplina.

    Exemplo:
        {% for d in disciplinas|filter_tipo_disciplina:"optativa" %}
            {{ d.nome }}
        {% endfor %}
    """
    return [d for d in disciplinas if d.tipo_disciplina == tipo]


@register.filter
def unique_tipos(disciplinas):
    """
    Retorna disciplinas com tipos únicos (sem repetição).

    Exemplo:
        {% for d in disciplinas|unique_tipos %}
            {{ d.tipo_disciplina }}
        {% endfor %}
    """
    vistos = set()
    unicos = []
    for d in disciplinas:
        if d.tipo_disciplina not in vistos:
            vistos.add(d.tipo_disciplina)
            unicos.append(d)
    return unicos


@register.filter
def get_item(dictionary, key):
    """
    Filtro personalizado para acessar valores de dicionários no template Django.

    Uso:
        {{ meu_dicionario|get_item:chave }}

    Exemplo:
        Se no contexto existir:
            meu_dicionario = {'nome': 'João'}

        Então no template:
            {{ meu_dicionario|get_item:'nome' }}
        exibirá:
            João

    Observação:
        Esse filtro é útil para acessar dicionários aninhados ou quando as chaves vêm de variáveis.
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None