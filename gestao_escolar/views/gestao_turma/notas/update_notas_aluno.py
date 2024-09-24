from django.shortcuts import render
from gestao_escolar.models import Trimestre, Matriculas, TurmaDisciplina



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
            notas = m.gestao_turmas_related.filter(grade=d, trimestre__in=trimestres_finais).values_list('notas', flat=True)
            print(f'o trimestre é {notas}')

            # Filtra notas que não são None
            notas_filtradas = [nota for nota in notas if nota is not None]

            if notas_filtradas and any(nota < 5 for nota in notas_filtradas):
                status = 'Reprovado'
            else:
                status = 'Aprovado'

            aluno_resultado['disciplinas'].append({
                'disciplina': d.disciplina.nome,
                'status': status
            })
            

    """
       resultados = []

    for m in matriculas:
        aluno_resultado = {
            'aluno': m.aluno.nome_completo,
            'disciplinas': []
        }
        
        for d in disciplinas:
            notas = m.gestao_turmas_related.filter(grade=d).values_list('notas', flat=True)

            if notas and any(nota < 5 for nota in notas):
                status = 'Reprovado'
            else:
                status = 'Aprovado'

            aluno_resultado['disciplinas'].append({
                'disciplina': d.disciplina.nome,
                'status': status
            })
    """
   

       
    

    context = {
        'matriculas': matriculas,
        'trimestre': trimestres,
        'disciplinas': disciplinas,
        'conteudo_page': f"Gestão Turmas - Notas Aluno",
    }
       
    return render(request, 'Escola/inicio.html', context)

