from django.shortcuts import redirect
from django.urls import reverse
from gestao_escolar.models import Matriculas, GestaoTurmas

def verifica_e_cria_gestao_turmas(request, pk):
    """
    # Obtém todos os alunos matriculados
    matriculas = Matriculas.objects.filter(turma=pk) 
    n = []
    # Itera sobre as matrículas e verifica se cada aluno já possui um registro em GestaoTurmas    
    for m in matriculas:
        n.append(m.id)
    
    for m in n: 
        if not GestaoTurmas.objects.filter(aluno= m):
            GestaoTurmas.objects.create(aluno = Matriculas.objects.get(pk = m)) """  
                 
    return redirect(reverse('Gestao_Escolar:gestao_turmas_update', kwargs={'pk': pk}))



