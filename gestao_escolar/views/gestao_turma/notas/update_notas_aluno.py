from django.shortcuts import render
from gestao_escolar.models import Trimestre, Matriculas, TurmaDisciplina, GestaoTurmas



def gestao_turmas_update_view(request, pk):
    matriculas = Matriculas.objects.filter(turma=pk)
    trimestres = Trimestre.objects.all()
    trimestres_finais = Trimestre.objects.filter(final=True) 
    

    disciplinas = TurmaDisciplina.objects.filter(turma=pk)
        
    for m in matriculas:
        aluno_resultado = {
            'aluno': m.aluno.nome_completo,
            'disciplinas': []
        }
        
        for d in disciplinas:
            # Filtra as notas para o trimestre final
            #notas = m.gestao_turmas_related.filter(grade=d, trimestre__in=trimestres_finais).values_list('notas', flat=True)
            notas = m.gestao_turmas_related.filter(trimestre__in=trimestres_finais).values_list('notas', flat=True)
            nota = m.gestao_turmas_related.filter(trimestre__in = trimestres_finais)
            todas_notas_finais = []
            for n in nota:
                todas_notas_finais.append([n.id, n.grade.disciplina ,n.trimestre, n.media_final])  
            
            notas_baixas = []
            for notas in todas_notas_finais:                
                if notas[3] < 5:
                    notas_baixas.append(notas[0])                

            for todos in todas_notas_finais:   
                if todos[3] < 5:  
                    status = 'Reprovado'
                    GestaoTurmas.objects.update(
                        aprovado = False                        
                    )
                    break
                else:
                    status = 'Aprovado'
                    GestaoTurmas.objects.update(
                        aprovado = True
                    )  

            aluno_resultado['disciplinas'].append({
                'disciplina': d.disciplina.nome,
                'status': status
            })

    context = {
        'matriculas': matriculas,
        'trimestre': trimestres,
        'disciplinas': disciplinas,
        'conteudo_page': f"Gestão Turmas - Notas Aluno",
    }
       
    return render(request, 'Escola/inicio.html', context)

