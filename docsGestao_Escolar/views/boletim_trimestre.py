from gestao_escolar.models import GestaoTurmas, Trimestre, TurmaDisciplina
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def boletim_trimestral(request, aluno_id, turma_id):
    aluno_boletim = GestaoTurmas.objects.filter(aluno=aluno_id, grade__turma=turma_id)
    trimestres = Trimestre.objects.all()
    grade = TurmaDisciplina.objects.filter(turma=turma_id)

    notas = []

    for t in trimestres:
        trimestre_info = {
            'trimestre_id': t.id,
            'trimestre_nome': t.numero_nome,
            'final': t.final,
            'disciplinas': []
        }

        # Filtrar as notas do aluno para o trimestre atual
        aluno_notas_trimestre = aluno_boletim.filter(trimestre=t)

        for g in grade:
            # Verifica se há notas para a disciplina no trimestre
            disciplina_info = {
                'disciplina_nome': g.disciplina.nome,
                'notas': None,
                'faltas': None,
                'parecer': None
            }
            # Encontrar a nota correspondente para a disciplina
            for a in aluno_notas_trimestre:
                if a.grade == g:
                    disciplina_info['notas'] = a.notas
                    disciplina_info['faltas'] = a.faltas
                    disciplina_info['parecer'] = a.parecer_descritivo
                    break

            trimestre_info['disciplinas'].append(disciplina_info)
        
        notas.append(trimestre_info)
 


    context = {
        'conteudo_page':"boletim_trimestral",   
        'titulo_page': "Boletim Escolar",
        'trimestres': trimestres,
        'notas': notas,
        'aluno': aluno_boletim

    }
    return render(request, 'Escola/inicio.html', context)

"""
        for g in grade:
            
        
        notas.append(trimestre_info)

    context = {
        'conteudo_page': "boletim_trimestral",
        'trimestres': trimestres,
        'notas': notas
    }
    return render(request, 'Escola/inicio.html', context)



"""