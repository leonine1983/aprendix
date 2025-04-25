from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from gestao_escolar.models import TurmaDisciplina, AnoLetivo, GestaoTurmas, Trimestre
from rh.models import Escola
from django.contrib import messages


# Create your views here.
@login_required
def home_professor(request):
    userProfessor = request.user.related_vinculoUserPessoa
    request.session['professorUser'] = userProfessor
    pessoa = userProfessor.pessoa.id     

    busca = request.GET.get('disciplina')
    if busca:
        notas = GestaoTurmas.objects.filter(grade__id = busca)
    else:
        notas = {}
   

    # Pequisa pra verifica se existe matricula feita do aluno
    professorGrade = TurmaDisciplina.objects.filter(professor__encaminhamento__contratado__id=pessoa)
    ano = AnoLetivo.objects.all()
    
    return render(request, 'modulo_professor/home.html', {
        'professor':professorGrade,
        'trimestre': Trimestre.objects.all(),
        'notas':notas,
        'anoLetivo': ano})


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