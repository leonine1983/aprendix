from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from gestao_escolar.models import GestaoTurmas, Matriculas, Trimestre, TurmaDisciplina
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum

@login_required
def create_or_update_Media_turmas(request, aluno_id):
    # Recupera o aluno usando o ID fornecido; retorna 404 se não encontrado
    aluno = get_object_or_404(Matriculas, pk=aluno_id)
    
    # Filtra as disciplinas associadas à turma do aluno
    disciplinas = TurmaDisciplina.objects.filter(turma=aluno.turma.id)
    
    # Obtém o trimestre específico (com ID 4)
    trimestre = Trimestre.objects.get(id=4)

    # Criar registros automaticamente ao carregar a página
    for disciplina in disciplinas:
        # Obtém ou cria um registro de gestão de turma para o aluno, trimestre e disciplina
        gestao_turma, created = GestaoTurmas.objects.get_or_create(aluno=aluno, trimestre=trimestre, grade=disciplina)
        print(f'essa é a turma da gestao {gestao_turma}')
        
        # Se o registro foi criado, registra o profissional responsável
        gestao_turma.profissional_resp = request.user.username
        
        # Atualiza a data e hora da modificação
        gestao_turma.data_hora_mod = timezone.now()

        # Calcula a soma das notas do aluno para a disciplina
        notas_aluno = GestaoTurmas.objects.filter(aluno=aluno, grade=disciplina).aggregate(Sum('notas'))
        print(f'notas do aluno {notas_aluno}')
        total_notas = notas_aluno['notas__sum']

        # Obtém o ano letivo da turma do aluno
        ano_letivo = aluno.turma.ano_letivo
        
        # Filtra os trimestres associados ao ano letivo
        trimestres = Trimestre.objects.filter(ano_letivo=ano_letivo)
        quant_trimestres = trimestres.count()  # Conta quantos trimestres existem

        if total_notas is not None:
            # Calcula a média final das notas, considerando o número de trimestres
            media_final = total_notas / (quant_trimestres - 1)
            gestao_turma.media_final = media_final  # Armazena a média final

        # Define o trimestre no registro de gestão da turma
        gestao_turma.trimestre = trimestre
        
        # Salva as alterações no banco de dados
        gestao_turma.save()


    # Mensagem de sucesso
    success_message = "Médias dos alunos foram atualizadas com sucesso!"
    messages.success(request, success_message)

    return redirect(reverse('Gestao_Escolar:gestao_turmas_update', kwargs={'pk': aluno.turma.pk}))


