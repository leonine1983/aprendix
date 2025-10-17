# Importa o módulo smtplib para envio de e-mails (não está sendo usado neste trecho)
import smtplib
# Importa a classe EmailMessage (também não utilizada aqui, mas poderia ser usada para envio de notificações)
from email.message import EmailMessage
from django.shortcuts import render
from gestao_escolar.models import Trimestre, Matriculas, TurmaDisciplina, GestaoTurmas
from django.contrib.auth.decorators import login_required

"""
@login_required
def gestao_turmas_update_view(request, pk):
    

    # Busca todas as matrículas da turma identificada por 'pk'
    matriculas = Matriculas.objects.filter(turma=pk)

    # Recupera todos os trimestres cadastrados
    trimestres = Trimestre.objects.all()

    # Filtra apenas os trimestres marcados como finais
    trimestres_finais = Trimestre.objects.filter(final=True) 
    
    # Busca todas as disciplinas da turma
    disciplinas = TurmaDisciplina.objects.filter(turma=pk)

    # Status padrão inicial para o aluno
    status = "Em análise"
        
    # Loop sobre todas as matrículas da turma
    for m in matriculas:
        # Cria um dicionário para armazenar o resultado de cada aluno
        aluno_resultado = {
            'aluno': m.aluno.nome_completo,
            'disciplinas': []
        }
        
        # Percorre todas as disciplinas da turma
        for d in disciplinas:
            # Busca todas as notas do aluno nos trimestres finais
            notas = m.gestao_turmas_related.filter(trimestre__in=trimestres_finais).values_list('notas', flat=True)

            # Recupera objetos GestaoTurmas correspondentes aos trimestres finais
            nota = m.gestao_turmas_related.filter(trimestre__in=trimestres_finais)

            # Lista para armazenar todas as notas finais formatadas
            todas_notas_finais = []
            for n in nota:
                # Cada item contém: ID do registro, nome da disciplina, trimestre e média final
                todas_notas_finais.append([n.id, n.grade.disciplina, n.trimestre, n.media_final])  
            
            # Lista para armazenar as notas consideradas baixas (<5)
            notas_baixas = []
            if todas_notas_finais:
                for notas in todas_notas_finais: 
                    # Verifica se existe média final e se é menor que 5
                    if notas[3]:               
                        if notas[3] < 5:
                            notas_baixas.append(notas[0])                

                # Agora percorre todas as notas finais para determinar o status geral
                for todos in todas_notas_finais:  
                    if todos[3]:  # Se há média final registrada
                        if todos[3] < 5:  # Caso a média seja menor que 5
                            status = 'Reprovado'
                            # Atualiza todos os registros GestaoTurmas como reprovado
                            GestaoTurmas.objects.update(
                                aprovado=False,
                                aluno__foi_a_recupera = True                        
                            )
                            break  # Interrompe o loop ao encontrar uma reprovação
                    if todos[3] is None:  # Caso a nota ainda não tenha sido lançada
                        status = 'Reprovado'
                        GestaoTurmas.objects.update(
                            aprovado=False,
                            aluno__foi_a_recupera = True                         
                        )
                        break

                    else:
                        # Caso todas as notas sejam suficientes
                        status = 'Aprovado'
                        GestaoTurmas.objects.update(
                            aprovado=True,
                            aluno__foi_a_recupera = False
                        )  

                # Adiciona a disciplina e o status do aluno ao dicionário de resultados
                aluno_resultado['disciplinas'].append({
                    'disciplina': d.disciplina.nome,
                    'status': status
                })
                

    # Monta o contexto que será enviado para o template
    context = {
        'matriculas': matriculas,
        'trimestre': trimestres,
        'disciplinas': disciplinas,
        'aluno_result': disciplinas,  # ⚠️ Talvez deveria ser 'aluno_resultado' (possível erro lógico)
        'conteudo_page': "Gestão Turmas - Notas Aluno",
    }
       
    # Renderiza o template HTML 'Escola/inicio.html' com os dados do contexto
    return render(request, 'Escola/inicio.html', context)
"""

# Importa o módulo smtplib para envio de e-mails (não está sendo usado neste trecho)
import smtplib
# Importa a classe EmailMessage (também não utilizada aqui, mas poderia ser usada para envio de notificações)
from email.message import EmailMessage
from django.shortcuts import render
from gestao_escolar.models import Trimestre, Matriculas, TurmaDisciplina, GestaoTurmas
from django.contrib.auth.decorators import login_required


@login_required
def gestao_turmas_update_view(request, pk):
    """
    View responsável por atualizar o status de aprovação dos alunos de uma turma específica.
    Ela verifica as notas finais e define se o aluno está 'Aprovado' ou 'Reprovado'.
    """

    # Busca todas as matrículas da turma identificada por 'pk'
    matriculas = Matriculas.objects.filter(turma=pk)

    # Recupera todos os trimestres cadastrados
    trimestres = Trimestre.objects.all()

    # Filtra apenas os trimestres marcados como finais
    trimestres_finais = Trimestre.objects.filter(final=True) 
    
    # Busca todas as disciplinas da turma
    disciplinas = TurmaDisciplina.objects.filter(turma=pk)

    # Status padrão inicial para o aluno
    status = "Em análise"
        
    # Loop sobre todas as matrículas da turma
    for m in matriculas:
        # Cria um dicionário para armazenar o resultado de cada aluno
        aluno_resultado = {
            'aluno': m.aluno.nome_completo,
            'disciplinas': []
        }
        
        # Percorre todas as disciplinas da turma
        for d in disciplinas:
            # Busca todas as notas do aluno nos trimestres finais
            notas = m.gestao_turmas_related.filter(trimestre__in=trimestres_finais).values_list('notas', flat=True)

            # Recupera objetos GestaoTurmas correspondentes aos trimestres finais
            nota = m.gestao_turmas_related.filter(trimestre__in=trimestres_finais)

            # Lista para armazenar todas as notas finais formatadas
            todas_notas_finais = []
            for n in nota:
                # Cada item contém: ID do registro, nome da disciplina, trimestre e média final
                todas_notas_finais.append([n.id, n.grade.disciplina, n.trimestre, n.media_final])  
            
            # Lista para armazenar as notas consideradas baixas (<5)
            notas_baixas = []
            if todas_notas_finais:
                for notas in todas_notas_finais: 
                    # Verifica se existe média final e se é menor que 5
                    if notas[3]:               
                        if notas[3] < 5:
                            notas_baixas.append(notas[0])                

                # Agora percorre todas as notas finais para determinar o status geral
                for todos in todas_notas_finais:  
                    if todos[3]:  # Se há média final registrada
                        if todos[3] < 5:  # Caso a média seja menor que 5
                            status = 'Reprovado'

                            # Atualiza a matrícula do aluno (não o GestaoTurmas)
                            m.aprovado = False
                            m.foi_a_recupera = True
                            m.save()
                            break  # Interrompe o loop ao encontrar uma reprovação

                    if todos[3] is None:  # Caso a nota ainda não tenha sido lançada
                        status = 'Reprovado'
                        m.aprovado = False
                        m.foi_a_recupera = True
                        m.save()
                        break

                    else:
                        # Caso todas as notas sejam suficientes
                        status = 'Aprovado'
                        m.aprovado = True
                        m.foi_a_recupera = False
                        m.save()

                # Adiciona a disciplina e o status do aluno ao dicionário de resultados
                aluno_resultado['disciplinas'].append({
                    'disciplina': d.disciplina.nome,
                    'status': status
                })
                

    # Monta o contexto que será enviado para o template
    context = {
        'matriculas': matriculas,
        'trimestre': trimestres,
        'disciplinas': disciplinas,
        'aluno_result': disciplinas,  # ⚠️ Talvez deveria ser 'aluno_resultado'
        'conteudo_page': "Gestão Turmas - Notas Aluno",
    }
       
    # Renderiza o template HTML 'Escola/inicio.html' com os dados do contexto
    return render(request, 'Escola/inicio.html', context)
