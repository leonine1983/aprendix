from django.contrib.auth.decorators import login_required
from gestao_escolar.models import  TurmaDisciplina, AnoLetivo, GestaoTurmas, Trimestre, Matriculas, Presenca
from modulo_professor.models import ComposicaoNotas
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from collections import defaultdict
from rh.models import Escola


@login_required
def home_professor(request):
    userProfessor = request.user.related_vinculoUserPessoa
    request.session['professorUser'] = userProfessor
    pessoa = userProfessor.pessoa.id   

    trimestre = request.GET.get('trimestre')
    busca = request.GET.get('disciplina')   

    trimestreALL = Trimestre.objects.all()
    request.session['trimestres'] = trimestreALL
    
    if busca:
        request.session['escola']        
        trimestre_choice = Trimestre.objects.get(id=trimestre)
        final = trimestre_choice.final
        notas = GestaoTurmas.objects.filter(grade__id=busca, trimestre__id=trimestre)
        mural = "notas"

        grade = TurmaDisciplina.objects.get(id=busca)
        turma = grade.turma
        alunos = Matriculas.objects.filter(turma=turma)
        compoeNotas = ComposicaoNotas.objects.filter(grade=grade)

        notas_dict = {}
        for a in alunos:
            notas_dict = {}  # Reiniciado a cada aluno
            for t in trimestreALL:
                for ac in a.compoeNotaAlunos_related.all():
                    if ac.trimestre.id == t.id and ac.grade == grade:
                        aluno_id = ac.aluno.id
                        notas_dict[aluno_id] = {
                            'aluno_nome': ac.aluno.aluno,
                            'notas': {},
                            'trimestre': t.numero_nome,
                            'trimestre_id': t.id,
                            'media_final': ac.media_final
                        }
                        notas_dict[aluno_id]['notas'][t.id] = ac.nota_final
    else:
        notas_dict = {}
        mural = ""
        trimestre_choice = {}
        notas = {}  
        alunos = {}  
        compoeNotas = {}
        grade = {}
        final = False

    # Pesquisa se existe matrícula feita do aluno
    professorGrade = TurmaDisciplina.objects.filter(professor__encaminhamento__contratado__id=pessoa)
    request.session['turmaDisciplina'] = professorGrade
    ano = AnoLetivo.objects.all()

    # GRÁFICO 1: Faltas por mês (considerando disciplina do professor)
    faltas_por_mes = defaultdict(int)
    if professorGrade:
        presencas = Presenca.objects.filter(
            turma_disciplina__in=professorGrade,
            presente=False
        )

        for p in presencas:
            if p.data:
                mes_ano = p.data.strftime("%Y-%m")
                faltas_por_mes[mes_ano] += 1

    faltas_labels = sorted(faltas_por_mes.keys())
    faltas_values = [faltas_por_mes[mes] for mes in faltas_labels]

    # GRÁFICO 2: Médias de notas por trimestre
    notas_por_trimestre = defaultdict(list)
    medias_trimestres = []

    for grade in professorGrade:
        composicoes = ComposicaoNotas.objects.filter(grade=grade)
        for c in composicoes:
            if c.nota_final is not None:
                notas_por_trimestre[c.trimestre.numero_nome].append(c.nota_final)

    for trimestre_nome in sorted(notas_por_trimestre.keys()):
        notas = notas_por_trimestre[trimestre_nome]
        media = round(sum(notas) / len(notas), 2) if notas else 0
        medias_trimestres.append((trimestre_nome, media))

    notas_labels = [m[0] for m in medias_trimestres]
    notas_values = [m[1] for m in medias_trimestres]

    return render(request, 'modulo_professor/home.html', {
        'notas_dict': notas_dict,
        'final': final,        
        'professor': professorGrade,    
        'compoemNotas': compoeNotas,
        'notas': notas,
        'alunos': alunos,
        'mural': mural,
        'trimestre_choice': trimestre_choice,
        'grade': grade,
        'anoLetivo': ano,

        # Dados dos gráficos
        'faltas_labels': faltas_labels,
        'faltas_values': faltas_values,
        'notas_labels': notas_labels,
        'notas_values': notas_values,
    })





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
