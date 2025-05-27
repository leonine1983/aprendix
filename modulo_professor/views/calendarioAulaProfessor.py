from django.shortcuts import render, get_object_or_404
from gestao_escolar.models import Horario, TurmaDisciplina
from django.db.models import Q
from django.contrib.auth.decorators import login_required

@login_required
def dias_de_aula_professor(request, turma_disciplina_id):
    turma_disciplina = get_object_or_404(TurmaDisciplina, id=turma_disciplina_id)
    
    prof1 = turma_disciplina.professor.encaminhamento.contratado.id if turma_disciplina.professor else None
    prof2 = turma_disciplina.professo2.encaminhamento.contratado.id if turma_disciplina.professo2 else None
    prof3 = turma_disciplina.reserva_tecnica.encaminhamento.contratado.id if turma_disciplina.reserva_tecnica else None

    turmaAll = TurmaDisciplina.objects.filter(
        Q(professor__encaminhamento__contratado = prof1) or
        Q(professor__encaminhamento__contratado = prof2) or
        Q(professor__encaminhamento__contratado = prof3) 
        )
    """
    
    
    turma_disciplina = get_object_or_404(TurmaDisciplina, id=turma_disciplina_id)


    # Monta a query dinâmica
    query = Q(professor__encaminhamento__contratado=prof1)
    if prof2:
        query |= Q(professor__encaminhamento__contratado=prof2)
    if prof3:
        query |= Q(professor__encaminhamento__contratado=prof3)

    turmaAll = TurmaDisciplina.objects.filter(query).distinct()

    print(f'Professores relacionados: {prof1}, {prof2}, {prof3}')
    print(f'Turmas encontradas: {turmaAll}')
    
    
    """


    # Filtra horários da escola com validade ativa
    horarios = Horario.objects.filter(
        validade__escola_id=request.session['escola'].id,
        validade__horario_ativo=True
    )

    dias_da_semana = ['segunda', 'terca', 'quarta', 'quinta', 'sexta']
    dias_com_aula = []

    for horario in horarios:
        for dia in dias_da_semana:
            turma_do_dia = getattr(horario, dia)
            if turma_do_dia == turma_disciplina:
                dias_com_aula.append({
                    'dia': dia.capitalize(),
                    'turma': horario.turma.nome,
                    'periodo': horario.periodo
                })

    dias_com_aula.sort(key=lambda x: x['periodo'].hora_inicio)  # ordena por hora de início

    context = {
        'turma_disciplina': turma_disciplina,
        'dias_com_aula': dias_com_aula,
        'turmaAll': turmaAll
    }

    return render(request, 'modulo_professor/partial/calendario/dias_de_aula_professor.html', context)
