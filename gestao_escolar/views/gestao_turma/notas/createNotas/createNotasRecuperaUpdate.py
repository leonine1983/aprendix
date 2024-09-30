from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from gestao_escolar.models import GestaoTurmas, Matriculas, Trimestre, TurmaDisciplina
from django import forms
from django.core.validators import MaxValueValidator
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages

class GestaoTurmasForm(forms.ModelForm):
    recuperacao_final = forms.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MaxValueValidator(10.00, message="O valor não pode ser maior que 10.00.")],
        required=False
    )
    
    class Meta:
        model = GestaoTurmas
        fields = ['recuperacao_final']



""" A view em função tem como objetivo cadastrar as notas dos alunos e calcular automaticamente a média.
 Ela permite a entrada de múltiplas notas, valida os dados e assegura o armazenamento eficiente. 
 A média é calculada conforme as regras definidas, facilitando o controle do desempenho acadêmico e simplificando relatórios para os professores.
"""
@login_required
def create_or_update_gestao_turmas_recupera(request, aluno_id, trimestre_id):
    aluno = get_object_or_404(Matriculas, pk=aluno_id)
    trimestre = get_object_or_404(Trimestre, pk=trimestre_id)
    disciplinas = TurmaDisciplina.objects.filter(turma=aluno.turma.id)
    notas_recupera = []

    if request.method == 'POST':
        for disciplina in disciplinas:
            gestao_turma, created = GestaoTurmas.objects.get_or_create(aluno=aluno, trimestre=trimestre, grade=disciplina)
            form = GestaoTurmasForm(request.POST, instance=gestao_turma, prefix=disciplina.disciplina)

            if form.is_valid():
                form.instance.profissional_resp = request.user.username
                form.instance.data_hora_mod = timezone.now()
                form.save()
                
                # Armazenar a nota de recuperação
                notas_recupera.append(form.instance.recuperacao_final)

                # Verificar se todas as notas são maiores que 5  
                print(f"olha o texto {notas_recupera}")   
                try: 
                    if all(nota >= 5 for nota in notas_recupera):
                        status = "Aprovado na recuperação"
                        aluno.aprovado_recupera = True
                        aluno.naoFoi_a_recupera = False
                    else:
                        status = "Reprovado na recuperação"
                        aluno.aprovado_recupera = False
                        aluno.naoFoi_a_recupera = False
                    aluno.save()
                except Exception as e:
                    status = "Indefinido"
                    aluno.naoFoi_a_recupera = True
                    aluno.aprovado_recupera = False
                    aluno.save()
                    print(f"Erro ao verificar notas {e}")

        success_message = f"Notas de Recuperação do aluno {aluno.aluno} foram atualizadas com sucesso! Status: {status}"
        messages.info(request, success_message)        
        return redirect(reverse('Gestao_Escolar:create_or_update_media_turmas', kwargs={'aluno_id': aluno.pk}))

    else:
        forms_dict = {}
        for disciplina in disciplinas:
            gestao_turma, created = GestaoTurmas.objects.get_or_create(aluno=aluno, trimestre=trimestre, grade=disciplina)
            initial_data = {'nota': gestao_turma.recuperacao_final} if gestao_turma else None
            forms_dict[disciplina.disciplina] = GestaoTurmasForm(instance=gestao_turma, prefix=disciplina.disciplina, initial=initial_data)

    context = {
        'forms_dict': forms_dict,
        'aluno': aluno,
        'trimestre': trimestre,
        'conteudo_page': "Gestão Turmas - Notas Recupera Update",
    }

    return render(request, 'Escola/inicio.html', context)
