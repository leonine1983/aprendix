from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from gestao_escolar.models import Turmas, TurmaDisciplina, AnoLetivo, GestaoTurmas, Trimestre, Matriculas, Presenca
from rh.models import Escola
from .models import ComposicaoNotas
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django import forms



# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from gestao_escolar.models import Turmas, TurmaDisciplina, AnoLetivo, GestaoTurmas, Trimestre, Matriculas, Presenca
from rh.models import Escola
from .models import ComposicaoNotas
from django.contrib import messages
from django.db.models import Count, Q, Avg
from collections import defaultdict
from datetime import datetime


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




class ComposicaoNotasForm(forms.ModelForm):
    class Meta:
        model = ComposicaoNotas
        fields = [ 'prova', 'trabalho', 'participacao', 'tarefas', 'anotacoes', 'prova_paralela']
        widgets = {
            'anotacoes': forms.Textarea(attrs={'rows': 3}),
        }


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect

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

            # Recupera os valores simulando um GET
            trimestre_valor = trimestre_obj.id
            disciplina_valor = grade_obj.id 
            # Monta a URL com parâmetros GET
            url = reverse("modulo_professor:homeProfessor")
            query_string = f"?trimestre={trimestre_valor}&disciplina={disciplina_valor}"
            full_url = f"{url}{query_string}"
            return HttpResponseRedirect(full_url)

    else:
        form = ComposicaoNotasForm(instance=composicao_existente)

    return render(request, "modulo_professor/partial/notas/notas.html", {
        "form": form,
        'grade': grade_obj,
        'aluno': aluno_obj
    })





class ComposicaoRecuperaForm(forms.ModelForm):
    class Meta:
        model = ComposicaoNotas
        fields = ['recuperacao_final']  # adicione outros campos se quiser exibir mais


def atualizaRecuperaFinal(request, pk, grade):
    # Obtém o trimestre final
    try:
        tFinal = Trimestre.objects.get(final=True)
    except Trimestre.DoesNotExist:
        messages.error(request, "Trimestre final não está configurado.")
        return redirect('sua_view_de_erro')  # Redirecione apropriadamente

    # Obtém ou cria ComposicaoNotas para esse aluno/grade no trimestre final
    aluno = get_object_or_404(Matriculas, pk=pk)
    grade_disc = get_object_or_404(TurmaDisciplina, pk=grade)

    comp, created = ComposicaoNotas.objects.get_or_create(
        aluno=aluno,
        grade=grade_disc,
        trimestre=tFinal
    )

    if request.method == 'POST':
        form = ComposicaoRecuperaForm(request.POST, instance=comp)
        if form.is_valid():
            form.save()
            messages.success(request, f"Recuperação final atualizada com sucesso. Aluno {aluno}")
            return redirect('modulo_professor:homeProfessor')  # Redirecione após salvar
        else:
            messages.error(request, "Erro ao salvar os dados. Verifique o formulário.")
    else:
        form = ComposicaoRecuperaForm(instance=comp)

    context = {
        'form': form,
        'aluno': aluno,
        'grade': grade_disc,
        'composicao': comp,
        'criado': created
    }

    return render(request, 'modulo_professor/partial/recuperação/recuperaFinal.html', context)


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


# PRESENÇA ------------------------------------------------------------------

# PRESENÇA DIÁRIA ------------------------
@login_required
def registrar_presenca_diaria_view(request, turma_id):
    turma = get_object_or_404(Turmas, id=turma_id)
    matriculas = Matriculas.objects.filter(turma=turma)

    if request.method == 'POST':
        data_presenca_str = request.POST.get('data')
        try:
            data_presenca = datetime.strptime(data_presenca_str, '%Y-%m-%d').date()
        except ValueError:
            return render(request, 'modulo_professor/partial/presenca/presenca_diaria.html', {
                'matriculas': matriculas,
                'turma': turma,
                'today': date.today(),
                'erro': 'Data inválida. Use o formato yyyy-mm-dd.'
            })

        alunos_presentes_ids = request.POST.getlist('presentes')
        for matricula in matriculas:
            presente = str(matricula.id) in alunos_presentes_ids
            Presenca.objects.update_or_create(
                matricula=matricula,
                data=data_presenca,
                turma_disciplina=None,
                aula_numero=None,
                defaults={'presente': presente, 'controle_diario': True}
            )
        return redirect('modulo_professor:lista_presenca_diaria', turma.id, data_presenca.strftime('%Y-%m-%d'))


    return render(request, 'modulo_professor/partial/presenca/presenca_diaria.html', {
        'matriculas': matriculas,
        'turma': turma,
        'today': date.today()
    })


@login_required
def lista_presenca_diaria_view(request, turma_id, data_str):
    turma = get_object_or_404(Turmas, id=turma_id)
    data_presenca = datetime.strptime(data_str, '%Y-%m-%d').date()
    
    presencas = Presenca.objects.filter(turma_disciplina=None, controle_diario=True, data=data_presenca, matricula__turma=turma)

    alunos_presentes = presencas.filter(presente=True)
    alunos_faltosos = presencas.filter(presente=False)

    return render(request, 'modulo_professor/partial/presenca/lista_presenca_diaria.html', {
        'turma': turma,
        'data': data_presenca,
        'presentes': alunos_presentes,
        'faltosos': alunos_faltosos,
    })




# ------- Mostra faltas -------------------------
from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from datetime import datetime

from django.shortcuts import render

@login_required
def historico_faltas_view(request, matricula_id):
    matricula = get_object_or_404(Matriculas, id=matricula_id)
    presencas = Presenca.objects.filter(matricula=matricula).order_by('data')

    faltas_por_mes = defaultdict(lambda: [None]*31)  # 31 dias no máximo

    for presenca in presencas:
        if not presenca.presente:
            mes = presenca.data.month
            dia = presenca.data.day
            faltas_por_mes[mes][dia - 1] = 'F'  # 'F' para Falta

    # Gerando intervalo de dias para passar ao template
    dias_do_mes = list(range(1, 32))  # Dias de 1 a 31

    return render(request, 'modulo_professor/partial/presenca/historico_faltasDias.html', {
        'matricula': matricula,
        'faltas_por_mes': dict(faltas_por_mes),
        'dias_do_mes': dias_do_mes,
    })




# PRESENÇA POR AULA
@login_required
def selecionaTurma(request):
    userProfessor = request.user.related_vinculoUserPessoa
    pessoa = userProfessor.pessoa.id  
    professorGrade = TurmaDisciplina.objects.filter(professor__encaminhamento__contratado__id=pessoa)
    return render(request, 'modulo_professor/partial/presenca/selecionaTurma.html', {'pessoa':professorGrade})



# PRESENÇA POR DISCIPLINA
@login_required
def selecionaTurmaDisciplina(request):
    userProfessor = request.user.related_vinculoUserPessoa
    pessoa = userProfessor.pessoa.id  
    professorGrade = TurmaDisciplina.objects.filter(professor__encaminhamento__contratado__id=pessoa)
    return render(request, 'modulo_professor/partial/presenca/selecionaTurmaDisciplina.html', {'pessoa':professorGrade})




from datetime import date

@login_required
def registrar_presenca_por_aula_view(request, turma_disciplina_id):
    turma_disciplina = get_object_or_404(TurmaDisciplina, id=turma_disciplina_id)
    turma = turma_disciplina.turma
    matriculas = Matriculas.objects.filter(turma=turma)

    if request.method == 'POST':
        data_presenca_str = request.POST.get('data')
        aula_numero = request.POST.get('aula_numero')
        alunos_presentes_ids = request.POST.getlist('presentes')
        data_presenca = data_presenca_str

        # Registro das presenças por aula
        for matricula in matriculas:
            presente = str(matricula.id) in alunos_presentes_ids
            try:
                Presenca.objects.update_or_create(
                    matricula=matricula,
                    data=data_presenca,
                    turma_disciplina=turma_disciplina,
                    aula_numero=aula_numero,
                    defaults={'presente': presente, 'controle_diario': False}
                )
                messages.success(request, "Frequência diária realizada com sucesso!!!")
            except Exception as e:
                print(f"Erro ao registrar presença para matrícula {matricula.id}: {e}")



    # Envia a data atual formatada como dd/mm/aaaa
    today = date.today()
    data_formatada = today.strftime('%d/%m/%Y')


    return render(request, 'modulo_professor/partial/presenca/presenca_por_aula.html', {
    'matriculas': matriculas,
    'turma_disciplina': turma_disciplina,
    'data': data_formatada,
    'today': today,
    })



from collections import defaultdict

@login_required
def faltas_por_disciplina_mes_view(request, turma_disciplina_id):
    turma_disciplina = get_object_or_404(TurmaDisciplina, id=turma_disciplina_id)
    turma = turma_disciplina.turma
    matriculas = Matriculas.objects.filter(turma=turma)

    mes_param = request.GET.get('mes')
    if mes_param:
        try:
            mes = datetime.strptime(mes_param, "%Y-%m")
        except ValueError:
            mes = datetime.today()
    else:
        mes = datetime.today()

    inicio_mes = mes.replace(day=1)
    if mes.month == 12:
        fim_mes = mes.replace(year=mes.year + 1, month=1, day=1)
    else:
        fim_mes = mes.replace(month=mes.month + 1, day=1)

    presencas = Presenca.objects.filter(
        turma_disciplina=turma_disciplina,
        data__gte=inicio_mes,
        data__lt=fim_mes,
        presente=False
    ).order_by('data')

    # Armazena as faltas detalhadas: {matricula: [(data, numero_aula), ...]}
    faltas_detalhadas = defaultdict(list)
    for presenca in presencas:
        faltas_detalhadas[presenca.matricula].append((presenca.data, presenca.aula_numero))

    return render(request, 'modulo_professor/partial/presenca/faltas_por_disciplina_mes.html', {
        'turma_disciplina': turma_disciplina,
        'faltas_detalhadas': dict(faltas_detalhadas),
        'mes': mes.strftime('%Y-%m')
    })
