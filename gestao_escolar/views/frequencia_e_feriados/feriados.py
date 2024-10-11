from django.shortcuts import render
from datetime import datetime, timedelta
import holidays
from rh.models import Feriado, Encaminhamentos, Escola, Ano
from django.contrib.auth.decorators import login_required

@login_required
def calendario_mes(request, ano=datetime.now().year, mes=datetime.now().month):
    hoje = datetime(ano, mes, 1)
    dias_no_mes = (hoje.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

    # Profissionais que terão o frequencia impressa
    escola = Escola.objects.get(id = request.session['escola_id'])
    ano_l = Ano.objects.get(id = request.session['anoLetivo_id'])
    profissionais = Encaminhamentos.objects.filter(destino = escola, encaminhamento__ano_contrato = ano_l)

    # Obtendo feriados nacionais
    feriados_nacionais = holidays.Brazil(years=ano)

    # Obtendo feriados locais
    feriados_locais = Feriado.objects.filter(data__year=ano, data__month=mes)

    # Mapeando os dias da semana para português
    dias_da_semana = {
        0: 'Segunda-feira',
        1: 'Terça-feira',
        2: 'Quarta-feira',
        3: 'Quinta-feira',
        4: 'Sexta-feira',
        5: 'Sábado',
        6: 'Domingo'
    }

    dias = []
    for dia in range(1, dias_no_mes.day + 1):
        data_atual = hoje.replace(day=dia)
        feriado_nacional = data_atual.date() in feriados_nacionais
        feriado_nacional_nome = feriados_nacionais.get(data_atual.date()) if feriado_nacional else None
        feriado_local = feriados_locais.filter(data=data_atual.date()).exists()
        feriado_local_nome = feriados_locais.filter(data=data_atual.date())

        # Mapeando o índice do dia da semana para o nome em português
        dia_da_semana = dias_da_semana[data_atual.weekday()]

        dias.append({
            'data': data_atual,
            'feriado_nacional': feriado_nacional,
            'feriado_nacional_nome': feriado_nacional_nome,
            'feriado_local': feriado_local,
            'feriado_local_nome': feriado_local_nome,
            'final_de_semana': data_atual.weekday() >= 5,  # Sábado ou Domingo
            'dia_da_semana': dia_da_semana,
            
        })

    return render(request, 'Escola/inicio.html', {'dias': dias, 'ano': ano, 'mes': mes, 'conteudo_page': "freqenciaImpressa", 'profissionais': profissionais,})
