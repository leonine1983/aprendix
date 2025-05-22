from django.contrib.auth.decorators import login_required
from gestao_escolar.models import Turmas, TurmaDisciplina, AnoLetivo, GestaoTurmas, Trimestre, Matriculas, Presenca, ParecerDescritivo
from rh.models import Escola
from .models import ComposicaoNotas
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django import forms

from collections import defaultdict
from datetime import datetime

from g4f.client import Client
from django.http import JsonResponse
from django.utils.safestring import mark_safe

from django.urls import reverse
from django.http import HttpResponseRedirect
from datetime import date
from django.urls import reverse_lazy


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
            except Exception as e:
                print(f"Erro ao registrar presença para matrícula {matricula.id}: {e}")
        messages.success(request, "Frequência diária realizada com sucesso!!!")
        return redirect('modulo_professor:faltas_por_disciplina_mes', turma_disciplina_id=turma_disciplina.id)

    # Envia a data atual formatada como dd/mm/aaaa
    today = date.today()
    data_formatada = today.strftime('%d/%m/%Y')

    return render(request, 'modulo_professor/partial/presenca/presenca_por_aula.html', {
    'matriculas': matriculas,
    'turma_disciplina': turma_disciplina,
    'data': data_formatada,
    'today': today,
    })


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
        'mes': mes.strftime('%Y-%m'),
        'hoje': date.today(),
    })


# parecer descritivo do aluno
# ---------------------------------------------------------------
from django import forms
from gestao_escolar.models import ParecerDescritivo

class ParecerDescritivoForm(forms.ModelForm):
    class Meta:
        model = ParecerDescritivo
        fields = [
            'aspectos_cognitivos',
            'aspectos_socioemocionais',
            'aspectos_fisicos_motoras',
            'habilidades',
            'conteudos_abordados',
            'interacao_social',
            'comunicacao',
            'consideracoes_finais',
            'observacao_coordenador',
            'resumo',
        ]
        widgets = {
            field: forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}) for field in fields
        }

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from gestao_escolar.models import ParecerDescritivo, Trimestre, Matriculas
from g4f.client import Client  # Assumindo que está usando isso
# ...

@login_required
def parecerTurma(request, turma):
    turma = Matriculas.objects.filter(turma=turma)
    trimestre=Trimestre.objects.all()
    return render (request, 'modulo_professor/partial/parecerDescritivo/parecerTurma.html', {'trimestre':trimestre, 'turma':turma })


@login_required
def alunoGestaoTurmasParecer(request, pk, trimestre):    
    matricula = get_object_or_404(Matriculas, pk=pk)
    trimestre_obj = get_object_or_404(Trimestre, pk=trimestre)
    trimestre=Trimestre.objects.all()
    parecerAlunoImpressao = ParecerDescritivo.objects.filter(matricula = pk).order_by('trimestre__id')

    parecer, created = ParecerDescritivo.objects.get_or_create(matricula=matricula, trimestre=trimestre_obj)
    autor = f"Professor(a) {request.user.related_vinculoUserPessoa}"
    

    if request.method == 'POST':
        form = ParecerDescritivoForm(request.POST, instance=parecer)
        if form.is_valid():
            parecer = form.save()

            # Geração de resumo com IA
            pAtrib = {
                'aluno': parecer.matricula.aluno,
                'idade': parecer.matricula.aluno.idade,
                'genero': parecer.matricula.aluno.sexo,
                'trimestre': parecer.trimestre,
            }

            message_resumo = [
                "Por favor, com base nas informações a seguir sobre o aluno, elabore um parecer descritivo com no mínimo 500 caracteres abordando suas habilidades acadêmicas, comportamento, participação em sala de aula e áreas de melhoria.",
                f'Nome do Aluno: {pAtrib["aluno"]}',
                f'Idade: {pAtrib["idade"]} anos',
                f'Gênero: {pAtrib["genero"]}',
                f'Trimestre atual: {pAtrib["trimestre"]}',
                f'Aspectos Cognitivos: {parecer.aspectos_cognitivos}',
                f'Aspectos Socioemocionais: {parecer.aspectos_socioemocionais}',
                f'Aspectos Físicos/Motoras: {parecer.aspectos_fisicos_motoras}',
                f'Habilidades: {parecer.habilidades}',
                f'Conteúdos Abordados: {parecer.conteudos_abordados}',
                f'Interação Social: {parecer.interacao_social}',
                f'Comunicação: {parecer.comunicacao}',
                f'Considerações Finais: {parecer.consideracoes_finais}',
                f'Observação do Coordenador: {parecer.observacao_coordenador}',
            ]

            client = Client()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "\n".join(message_resumo)}]
            )

            resumo = response.choices[0].message.content
            parecer.resumo = resumo

            if created:
                parecer.author_created = autor
            else:
                parecer.author_atualiza = autor
            parecer.save()
            
            messages.success(request, f"O parecer do aluno {parecer.matricula} referente ao {parecer.trimestre} foi salvo com sucesso.")
            return redirect('modulo_professor:aluno_parecer', pk=parecer.matricula.id, trimestre=parecer.trimestre.id)

    else:
        form = ParecerDescritivoForm(instance=parecer)

    context = {
        'form': form,
        'aluno': matricula.aluno,
        'trimestre': trimestre_obj,
        'trimestres': trimestre,
        'matricula': matricula,
        'parecer': parecer,
        'parecerAlunoImpressao':parecerAlunoImpressao,
    }
    return render(request, 'modulo_professor/partial/parecerDescritivo/create_parecer.html', context)


def atualizarResumoFinal(request, pk):
    trimestres = Trimestre.objects.filter(final=False)
    infoAll = {
        'aspectos_cognitivos': [],
        'aspectos_socioemocionais': [],
        'aspectos_fisicos_motoras': [],
        'habilidades': [],
        'conteudos_abordados': [],
        'interacao_social': [],
        'comunicacao': [],
        'consideracoes_finais': [],
        'observacao_coordenador': [],
        'resumo': []
    }

    for trimestre in trimestres:
        pareceres = ParecerDescritivo.objects.filter(matricula=pk, trimestre=trimestre)
        for p in pareceres:
            infoAll['aspectos_cognitivos'].append(f'No {p.trimestre}, {p.aspectos_cognitivos}')
            infoAll['aspectos_socioemocionais'].append(f'No {p.trimestre}, {p.aspectos_socioemocionais}')
            infoAll['aspectos_fisicos_motoras'].append(f'No {p.trimestre}, {p.aspectos_fisicos_motoras}')
            infoAll['habilidades'].append(f'No {p.trimestre}, {p.habilidades}')
            infoAll['conteudos_abordados'].append(f'No {p.trimestre}, {p.conteudos_abordados}')
            infoAll['interacao_social'].append(f'No {p.trimestre}, {p.interacao_social}')
            infoAll['comunicacao'].append(f'No {p.trimestre}, {p.comunicacao}')
            infoAll['consideracoes_finais'].append(f'No {p.trimestre}, {p.consideracoes_finais}')
            infoAll['observacao_coordenador'].append(f'No {p.trimestre}, {p.observacao_coordenador}')
            infoAll['resumo'].append(f'No {p.trimestre}, {p.resumo}')

    parecer_final = ParecerDescritivo.objects.get(matricula=pk, trimestre__final=True)
    texto_orientado = f"Analise o texto sobre o comportamento do aluno {parecer_final.matricula} faça um resumo e em seguida, forneça orientações práticas para o professor em 2º pessoa. Crie uma história fictícia que possa fazer o professor entender como ajudar o aluno. Máximo 500 caracteres"
    texto_resumo = f"Analise o texto e faça um resumo. Dependendo do que foi escrito dê orientações ao profissional. "

    # Cria as mensagens para cada campo
    aspectos_cognitivos = f"{texto_orientado}: {infoAll.get('aspectos_cognitivos')}"
    aspectos_socio = f"{texto_orientado}: {infoAll.get('aspectos_socioemocionais')}"
    aspectos_fisic = f"{texto_orientado}: {infoAll.get('aspectos_fisicos_motoras')}"
    aspectos_habil = f"{texto_orientado}: {infoAll.get('habilidades')}"
    aspectos_conteu = f"{texto_orientado}: {infoAll.get('conteudos_abordados')}"
    aspectos_inter = f"{texto_orientado}: {infoAll.get('interacao_social')}"
    aspectos_comun = f"{texto_orientado}: {infoAll.get('comunicacao')}"
    aspectos_conside = f"{texto_resumo}: {infoAll.get('consideracoes_finais')}"
    aspectos_obs = f"{texto_resumo}: {infoAll.get('observacao_coordenador')}"
    aspectos_resumo = f"Crie um Parecer Descritivo Geral do aluno {parecer_final.matricula} com base nos pareceres que foram criados ao longo do trimestre: {infoAll.get('resumo')}"

    client = Client()

    # Realiza chamadas para o modelo para cada aspecto
    responses = {}
    for key, content in {
        'cognitivo': aspectos_cognitivos,
        'socio': aspectos_socio,
        'fisico': aspectos_fisic,
        'habilidade': aspectos_habil,
        'conteudo': aspectos_conteu,
        'interacao': aspectos_inter,
        'comunicacao': aspectos_comun,
        'consideracoes': aspectos_conside,
        'observacao': aspectos_obs,
        'resumo': aspectos_resumo
    }.items():
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": f"{content}\n\nPor favor, forneça as orientações em português."
            }]
        )
        responses[key] = response.choices[0].message.content

    # Atualiza ou cria o parecer descritivo final
    ParecerDescritivo.objects.update_or_create(
        matricula=pk, 
        trimestre__final=True,
        defaults={
            'aspectos_cognitivos': responses['cognitivo'],
            'aspectos_socioemocionais': responses['socio'],
            'aspectos_fisicos_motoras': responses['fisico'],
            'habilidades': responses['habilidade'],
            'conteudos_abordados': responses['conteudo'],
            'interacao_social': responses['interacao'],
            'comunicacao': responses['comunicacao'],
            'consideracoes_finais': responses['consideracoes'],
            'observacao_coordenador': responses['observacao'],
            'resumo': responses['resumo']
        }
    )

    # Retorna o resultado como JSON
    return JsonResponse({
        'resumo_cognitivo': mark_safe(responses['cognitivo']),
        'resumo_socioemocional': mark_safe(responses['socio']),
        # Adicione outros dados que você deseja retornar
    })
 


# Diario de Classe -----------------

from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from .models import PlanoDeAula
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from .models import PlanoDeAula
from django.db.models import Q
from django.db.models import Q
from .models import TurmaDisciplina
from rh.models import Encaminhamentos, UserPessoas
from django import forms
from .models import PlanoDeAula
from django.db.models import Q

class PlanoDeAulaForm(forms.ModelForm):
    class Meta:
        model = PlanoDeAula
        fields = '__all__'
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'conteudo_planejado': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'objetivo_geral': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'competencias_bncc': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'habilidades_bncc': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'metodologia': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'recursos_didaticos': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if request:
            escola = request.session.get('escola')
            user = request.user

            try:
                pessoa = UserPessoas.objects.get(user=user).pessoa
                encaminhamentos = Encaminhamentos.objects.filter(encaminhamento__contratado=pessoa)

                self.fields['turma_disciplina'].queryset = TurmaDisciplina.objects.filter(
                    Q(professor__in=encaminhamentos) |
                    Q(professo2__in=encaminhamentos) |
                    Q(reserva_tecnica__in=encaminhamentos) |
                    Q(auxiliar_classe__in=encaminhamentos),
                    turma__escola=escola
                ).distinct()

            except UserPessoas.DoesNotExist:
                self.fields['turma_disciplina'].queryset = TurmaDisciplina.objects.none()




from django.db.models import Q
from modulo_professor.models import TurmaDisciplina
from rh.models import UserPessoas, Encaminhamentos

from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from modulo_professor.models import TurmaDisciplina, PlanoDeAula
from rh.models import UserPessoas, Encaminhamentos, Contrato


class PlanoDeAulaCreateView(LoginRequiredMixin, CreateView):
    model = PlanoDeAula
    form_class = PlanoDeAulaForm
    template_name = 'modulo_professor/partial/diario/planoAula/createPlano.html'
    success_url = reverse_lazy('modulo_professor:plano_de_aula_criar')  # redireciona para mesma view

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = self.request.session.get('escola')
        usuario = self.request.user
        pessoa = get_object_or_404(UserPessoas, user = usuario)

        if escola and usuario:
            try:
                pessoa = UserPessoas.objects.get(user=usuario).pessoa
            except UserPessoas.DoesNotExist:
                pessoa = None

            if pessoa:
                planos = PlanoDeAula.objects.filter(
                    turma_disciplina__professor__encaminhamento__contratado__id=pessoa.id,
                    turma_disciplina__turma__escola__id=escola.id
                ).distinct()
            else:
                planos = PlanoDeAula.objects.none()
        else:
            planos = PlanoDeAula.objects.none()

        context['planos'] = planos
        return context


    def form_valid(self, form):
        print("FORM VALID - POST recebido com sucesso!")
        response = super().form_valid(form)
        messages.success(self.request, "Plano de aula salvo com sucesso!")
        return response
    
    def form_invalid(self, form):
        # Captura os nomes legíveis dos campos com erro
        campos_com_erro = [form.fields[field].label or field for field in form.errors]

        # Cria uma mensagem amigável
        mensagem = "Por favor, é preciso preencher os seguintes campos obrigatórios: " + ", ".join(campos_com_erro)

        # Envia a mensagem de erro para o usuário
        messages.error(self.request, mensagem)
        return super().form_invalid(form)






from django.views.generic import UpdateView, DeleteView
from django.urls import reverse_lazy

class PlanoDeAulaUpdateView(LoginRequiredMixin, UpdateView):
    model = PlanoDeAula
    form_class = PlanoDeAulaForm
    template_name = 'modulo_professor/partial/diario/planoAula/createPlano.html'
    success_url = reverse_lazy('modulo_professor:plano_de_aula_criar') 

    def form_valid(self, form):
        response = super().form_valid(form)
        obj = form.instance
        messages.success(
            self.request,
            f'O plano de aula de {obj.data_inicio} a {obj.data_fim} para {obj.turma_disciplina} foi atualizado com sucesso.'
        )
        return response


class PlanoDeAulaDeleteView(LoginRequiredMixin, DeleteView):
    model = PlanoDeAula
    template_name = 'modulo_professor/partial/diario/planoAula/plano_de_aula_confirm_delete.html'
    success_url = reverse_lazy('modulo_professor:plano_de_aula_criar') 

    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f'O plano de aula de {obj.data_inicio} a {obj.data_fim} para {obj.turma_disciplina} foi excluído com sucesso.')
        return super().delete(request, *args, **kwargs)



# ----------------- AULA DIA ----------------------------------
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy
from .models import AulaDada, AnexoAula
from django import forms
from django import forms
from .models import AulaDada, PlanoDeAula
from django.db.models import Q

class AulaDadaForm(forms.ModelForm):
    class Meta:
        model = AulaDada
        fields = ['plano', 'turma_disciplina', 'data', 'hora_inicio', 'hora_fim', 'conteudo_dado', 'observacoes']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fim': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if request:
            escola = request.session.get('escola')
            user = request.user

            try:
                pessoa = UserPessoas.objects.get(user=user).pessoa
                encaminhamentos = Encaminhamentos.objects.filter(encaminhamento__contratado=pessoa)

                turmas_do_professor = TurmaDisciplina.objects.filter(
                    Q(professor__in=encaminhamentos) |
                    Q(professo2__in=encaminhamentos) |
                    Q(reserva_tecnica__in=encaminhamentos) |
                    Q(auxiliar_classe__in=encaminhamentos),
                    turma__escola=escola
                ).distinct()

                self.fields['turma_disciplina'].queryset = turmas_do_professor
                self.fields['plano'].queryset = PlanoDeAula.objects.filter(turma_disciplina__in=turmas_do_professor)

            except UserPessoas.DoesNotExist:
                self.fields['turma_disciplina'].queryset = TurmaDisciplina.objects.none()
                self.fields['plano'].queryset = PlanoDeAula.objects.none()



class AulaDadaCreateView(CreateView):
    model = AulaDada
    form_class = AulaDadaForm
    template_name = 'modulo_professor/partial/diario/aulaDia/criarAulaDia.html'
    success_url = reverse_lazy('modulo_professor:aula_dada_lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = self.request.session.get('escola')
        usuario = self.request.user
        pessoa = get_object_or_404(UserPessoas, user = usuario)

        if escola and usuario:
            try:
                pessoa = UserPessoas.objects.get(user=usuario).pessoa
            except UserPessoas.DoesNotExist:
                pessoa = None

            if pessoa:
                planos = AulaDada.objects.filter(
                    plano__turma_disciplina__professor__encaminhamento__contratado__id=pessoa.id,
                    turma_disciplina__turma__escola__id=escola.id
                ).distinct()
            else:
                planos = AulaDada.objects.none()
        else:
            planos = AulaDada.objects.none()

        context['aulaDada'] = planos
        return context


class AulaDadaDetailView(DetailView):
    model = AulaDada
    template_name = 'modulo_professor/aula_dada_detail.html'
    context_object_name = 'aula'

class AnexoAulaForm(forms.ModelForm):
    class Meta:
        model = AnexoAula
        fields = ['arquivo', 'descricao']

class AnexoAulaCreateView(CreateView):
    model = AnexoAula
    form_class = AnexoAulaForm
    template_name = 'modulo_professor/anexo_aula_form.html'

    def form_valid(self, form):
        form.instance.aula_id = self.kwargs['pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('modulo_professor:aula_dada_detalhe', kwargs={'pk': self.kwargs['pk']})












from django.shortcuts import render
from django.utils import timezone
from .models import AulaDada

def aulas_do_dia(request):
    hoje = timezone.now().date()

    # Busca todas as aulas dadas hoje
    aulas_hoje = AulaDada.objects.filter(data=hoje).select_related('plano', 'turma_disciplina')

    contexto_aulas = []

    for aula in aulas_hoje:
        # Presenças associadas à turma e data
        presencas = Presenca.objects.filter(
            turma_disciplina=aula.turma_disciplina,
            data=aula.data
        ).select_related('matricula__aluno')

        presentes = [p.matricula.aluno for p in presencas if p.presente]
        faltosos = [p.matricula.aluno for p in presencas if not p.presente]

        contexto_aulas.append({
            'aula': aula,
            'plano': aula.plano,
            'presentes': presentes,
            'faltosos': faltosos,
        })

    return render(request, 'modulo_professor/partial/diario/aulas_do_dia.html', {
        'aulas': contexto_aulas,
        'data_hoje': hoje,
    })

