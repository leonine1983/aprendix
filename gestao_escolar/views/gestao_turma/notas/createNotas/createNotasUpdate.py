from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from gestao_escolar.models import GestaoTurmas, Matriculas, Trimestre, TurmaDisciplina
from django import forms
from django.core.validators import MaxValueValidator
from django.utils import timezone
from django.contrib.auth.decorators import login_required

class GestaoTurmasForm(forms.ModelForm):
    notas = forms.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MaxValueValidator(10.00, message="O valor não pode ser maior que 10.00.")],
        required=False
    )
    
    class Meta:
        model = GestaoTurmas
        fields = ['notas', 'faltas']



""" A view em função tem como objetivo cadastrar as notas dos alunos e calcular automaticamente a média.
 Ela permite a entrada de múltiplas notas, valida os dados e assegura o armazenamento eficiente. 
 A média é calculada conforme as regras definidas, facilitando o controle do desempenho acadêmico e simplificando relatórios para os professores.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

@login_required
def create_or_update_gestao_turmas(request, aluno_id, trimestre_id):
    aluno = get_object_or_404(Matriculas, pk=aluno_id)
    trimestre = get_object_or_404(Trimestre, pk=trimestre_id)
    disciplinas = TurmaDisciplina.objects.filter(turma=aluno.turma.id)

    if request.method == 'POST':
        for disciplina in disciplinas:
            gestao_turma, created = GestaoTurmas.objects.get_or_create(
                aluno=aluno,
                trimestre=trimestre,
                grade=disciplina
            )
            form = GestaoTurmasForm(request.POST, instance=gestao_turma, prefix=disciplina.disciplina)

            if form.is_valid():
                instancia = form.save(commit=False)
                instancia.profissional_resp = request.user.username
                instancia.data_hora_mod = timezone.now()
                instancia._usuario_atual = request.user.username  # Define o usuário logado
                instancia.save()

        return redirect(reverse('Gestao_Escolar:create_or_update_media_turmas', kwargs={'aluno_id': aluno.pk}))

    else:
        forms_dict = {}
        for disciplina in disciplinas:
            gestao_turma, created = GestaoTurmas.objects.get_or_create(
                aluno=aluno,
                trimestre=trimestre,
                grade=disciplina
            )
            initial_data = {'nota': gestao_turma.notas, 'faltas': gestao_turma.faltas} if gestao_turma else None
            forms_dict[disciplina.disciplina] = GestaoTurmasForm(
                instance=gestao_turma,
                prefix=disciplina.disciplina,
                initial=initial_data
            )

    context = {
        'forms_dict': forms_dict,
        'aluno': aluno,
        'trimestre': trimestre,
        'conteudo_page': "Gestão Turmas - Notas Update",
    }

    return render(request, 'Escola/inicio.html', context)
