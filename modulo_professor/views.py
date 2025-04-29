from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from gestao_escolar.models import TurmaDisciplina, AnoLetivo, GestaoTurmas, Trimestre, Matriculas
from rh.models import Escola
from .models import ComposicaoNotas
from django.contrib import messages


# Create your views here.
@login_required
def home_professor(request):
    userProfessor = request.user.related_vinculoUserPessoa
    request.session['professorUser'] = userProfessor
    pessoa = userProfessor.pessoa.id   
    trimestre = request.GET.get('trimestre')
    busca = request.GET.get('disciplina')    
    
    if busca:
        request.session['escola']        
        trimestre_choice = Trimestre.objects.get(id=trimestre)
        notas = GestaoTurmas.objects.filter(grade__id = busca, trimestre__id = trimestre)
        mural = "notas"

        """
        Obtém todos os alunos matriculados em uma turma específica a partir de uma instância de TurmaDisciplina.
        Processo:
        1. Recupera o objeto `TurmaDisciplina` com base no ID passado em `busca`.
        2. Acessa a `turma` associada àquela instância de `TurmaDisciplina`.
        3. Filtra todas as matrículas (`Matriculas`) que estão relacionadas a essa turma específica.
        Resultado:
        Uma queryset contendo todos os alunos matriculados na turma correspondente à disciplina buscada.
        """
        grade = TurmaDisciplina.objects.get(id=busca)
        turma = grade.turma
        alunos = Matriculas.objects.filter(turma = turma )
        compoeNotas = ComposicaoNotas.objects.filter(grade = grade )

        notas_dict = {}
        for a in alunos:
            nota = ComposicaoNotas.objects.filter(
                aluno=a,
                grade=grade,
                trimestre=trimestre_choice
            ).first()
            notas_dict[a.id] = nota
    else:
        notas_dict = {}
        mural = ""
        trimestre_choice = {}
        notas = {}  
        alunos = {}  
        compoeNotas = {}
        grade = {}

    

    # Pequisa pra verifica se existe matricula feita do aluno
    professorGrade = TurmaDisciplina.objects.filter(professor__encaminhamento__contratado__id=pessoa)
    ano = AnoLetivo.objects.all()
    
    return render(request, 'modulo_professor/home.html', {
        'professor':professorGrade,
        'trimestre': Trimestre.objects.filter(final= False),        
        'compoemNotas': compoeNotas,
        'notas':notas,
        'alunos':alunos,
        'notas_dict': notas_dict,
        'mural': mural,
        'trimestre_choice':trimestre_choice,
        'grade':grade,
        'anoLetivo': ano})





from django import forms
from .models import ComposicaoNotas
class ComposicaoNotasForm(forms.ModelForm):
    class Meta:
        model = ComposicaoNotas
        fields = [ 'prova', 'trabalho', 'participacao', 'tarefas', 'anotacoes']
        widgets = {
            'anotacoes': forms.Textarea(attrs={'rows': 3}),
        }



from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def criaNotasComposicao(request, aluno, grade, trimestre):
    aluno_obj = get_object_or_404(Matriculas, id=aluno)
    grade_obj = get_object_or_404(TurmaDisciplina, id=grade)
    trimestre_obj = get_object_or_404(Trimestre, id=trimestre)

    composicao_existente = ComposicaoNotas.objects.filter(
        aluno=aluno_obj,
        grade=grade_obj,
        trimestre=trimestre_obj
    ).first()

    if request.method == "POST":
        form = ComposicaoNotasForm(request.POST, instance=composicao_existente)
        if form.is_valid():
            confirmar = request.POST.get("confirmar", "nao")

            if composicao_existente and confirmar != "sim":
                return render(request, "modulo_professor/partial/notas/confirmaAtualiza.html", {
                    "form": form,
                    "confirmar_pendente": True,
                })

            nova_instancia = form.save(commit=False)
            nova_instancia.aluno = aluno_obj
            nova_instancia.grade = grade_obj
            nova_instancia.trimestre = trimestre_obj
            nova_instancia.save()

            messages.success(request, "Notas do aluno foram salvas com sucesso!")
            return redirect("modulo_professor:homeProfessor")
    else:
        form = ComposicaoNotasForm(instance=composicao_existente)

    return render(request, "modulo_professor/partial/notas/notas.html", {"form": form})










@login_required
def home_sessaoIniciada(request):
    escola = request.POST.get('escola')
    ano_id = request.POST.get('ano')

    # Armazena os valor na sessao
    request.session['escola'] = Escola.objects.get(pk=escola)
    request.session['anoLetivo'] = AnoLetivo.objects.get(pk=ano_id)    

    escolaSession = request.session['escola'] 
    anoSession = request.session['anoLetivo']

    messages.success(request, f"A escola {escolaSession} foi iniciada com sucesso para o ano letivo de {anoSession}✨")   
    
    return redirect("modulo_professor:homeProfessor")












"""
request.session['escola_nome_query'] = escola


class TurmaDisciplina(models.Model):
    turma = models.ForeignKey(Turmas, related_name='gradeTurma_related', on_delete=models.CASCADE, null=True)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, null=True)
    quant_aulas_semana = models.IntegerField(default=5, null=True)
    quant_aulas_dia = models.IntegerField(default=3, null=True)
    professor = models.ForeignKey(Encaminhamentos, related_name='gradeProfessor1_related', on_delete=models.PROTECT, null=True)
    professo2 = models.ForeignKey(Encaminhamentos, related_name='gradeProfessor2_related', on_delete=models.PROTECT, null=True, blank=True)
    reserva_tecnica = models.ForeignKey(Encaminhamentos, related_name='reservaTecnica_related',on_delete=models.PROTECT,  null=True, blank=True)
    auxiliar_classe = models.ForeignKey(Encaminhamentos, related_name='auxiliarClasse_related',on_delete=models.PROTECT, null=True, blank=True)

    carga_horaria_anual = models.IntegerField(null=True)
    limite_faltas = models.IntegerField(null=True)

    def __str__(self):
        return f'{self.disciplina.nome} - {self.professor.encaminhamento}'

class Turmas(models.Model):
    nome = models.CharField(max_length=10)
    descritivo_turma = models.CharField(max_length=10, default='única')
    escola = models.ForeignKey('rh.Escola', on_delete=models.CASCADE)
    ano_letivo = models.ForeignKey(AnoLetivo, on_delete=models.CASCADE)
    serie =  models.ForeignKey(Serie_Escolar, on_delete=models.CASCADE)
    turno = models.CharField(choices=turno, null=False, default=1, max_length=12)        
    turma_multiserie = models.BooleanField(null=True, default=False)
    turma_concluida = models.BooleanField(null=True, default=False)
    quantidade_vagas = models.IntegerField(default=36) 
    vagas_disponiveis = models.IntegerField(null=True)



class GestaoTurmas(models.Model):
    aluno = models.ForeignKey(Matriculas, related_name='gestao_turmas_related', null=True, on_delete=models.CASCADE)
    grade = models.ForeignKey(TurmaDisciplina, null=True, related_name='grade_disciplina', on_delete=models.CASCADE)
    trimestre = models.ForeignKey(Trimestre, related_name='trimestre_related_turma', null=True, on_delete=models.CASCADE)
    notas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    faltas = models.IntegerField(null=True, blank=True)
    profissional_resp = models.CharField(max_length=40, null=True)





class GestaoTurmas(models.Model):
    aluno = models.ForeignKey(Matriculas, related_name='gestao_turmas_related', null=True, on_delete=models.CASCADE)
    grade = models.ForeignKey(TurmaDisciplina, null=True, related_name='grade_disciplina', on_delete=models.CASCADE)
    trimestre = models.ForeignKey(Trimestre, related_name='trimestre_related_turma', null=True, on_delete=models.CASCADE)
    notas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    faltas = models.IntegerField(null=True, blank=True)
    profissional_resp = models.CharField(max_length=40, null=True)
    data_hora_mod = models.DateTimeField(null=True)

    parecer_descritivo = models.TextField(max_length=500, default="Ainda não há parecer do aluno para esse período")

    faltas_total = models.IntegerField(null=True, blank=True)
    recuperacao_final = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    media_final = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)   

    media_anterior_conselho_classe = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    conselho_classe = models.BooleanField(default=False)

    aprovado = models.BooleanField(default=False)

"""