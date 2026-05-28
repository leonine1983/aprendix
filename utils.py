import qrcode
from django.http import HttpResponse
from io import BytesIO
from django.shortcuts import get_object_or_404


def gerar_qrcode_view(request, pk):
    from django.urls import reverse
    from merendaEscolar.models import Transferencia

    transferencia = get_object_or_404(Transferencia, pk=pk)

    url = reverse(
        "modulo_merendeiras:escola_receber_transfe",
        args=[transferencia.pk]
    )

    full_url = request.build_absolute_uri(url)

    qr = qrcode.make(full_url)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    return HttpResponse(buffer.getvalue(), content_type="image/png")




import calendar
from datetime import date


def semanas_do_mes(ano: int, mes: int) -> list[tuple[date, date]]:
    """
    Retorna uma lista de tuplas (inicio, fim) representando cada semana
    do calendário real do mês.

    Regras:
    - A semana 1 começa no dia 1 do mês.
    - Cada semana termina no domingo (isoweekday == 7),
      exceto a última, que termina no último dia do mês.
    - A semana seguinte começa na segunda-feira após o domingo anterior.
    - Resultado: entre 4 e 5 semanas por mês, jamais cruzando meses.

    Exemplos:
        Março/2026 → semana 1: 01–01 (só domingo)
                     semana 2: 02–08
                     semana 3: 09–15
                     semana 4: 16–22
                     semana 5: 23–31

        Abril/2026 → semana 1: 01–05 (qua→dom)
                     semana 2: 06–12
                     semana 3: 13–19
                     semana 4: 20–26
                     semana 5: 27–30
    """
    ultimo_dia_num = calendar.monthrange(ano, mes)[1]
    primeiro = date(ano, mes, 1)
    ultimo = date(ano, mes, ultimo_dia_num)

    semanas = []
    inicio_semana = primeiro

    while inicio_semana <= ultimo:
        # Domingo dessa semana (isoweekday 7)
        dias_ate_domingo = 7 - inicio_semana.isoweekday()
        fim_semana_natural = date(
            ano,
            mes,
            min(inicio_semana.day + dias_ate_domingo, ultimo_dia_num),
        )
        semanas.append((inicio_semana, fim_semana_natural))

        # Próxima semana começa na segunda seguinte
        proximo_inicio_dia = fim_semana_natural.day + 1
        if proximo_inicio_dia > ultimo_dia_num:
            break
        inicio_semana = date(ano, mes, proximo_inicio_dia)

    return semanas


def numero_semana_no_mes(hoje: date) -> int | None:
    """
    Retorna o número da semana (1-5) em que `hoje` se encontra
    dentro do próprio mês, ou None se não encontrado (não deve ocorrer).
    """
    semanas = semanas_do_mes(hoje.year, hoje.month)
    for numero, (inicio, fim) in enumerate(semanas, start=1):
        if inicio <= hoje <= fim:
            return numero
    return None