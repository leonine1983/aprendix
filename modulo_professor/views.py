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

@login_required
def alunoGestaoTurmasParecer(request, pk, trimestre):
    parecer = ParecerDescritivo.objects.filter(matricula=pk, trimestre=trimestre).first()  
    pAtrib = {
        'aluno': parecer.matricula,
        'idade': parecer.matricula.aluno.idade,
        'genero': parecer.matricula.aluno.sexo,
        'trimestre': parecer.trimestre,
        'aspectos_cognitivos': parecer.aspectos_cognitivos,
        'aspectos_socioemocionais': parecer.aspectos_socioemocionais,
        'aspectos_fisicos_motoras': parecer.aspectos_fisicos_motoras,
        'habilidades': parecer.habilidades,
        'conteudos_abordados': parecer.conteudos_abordados,
        'interacao_social': parecer.interacao_social,
        'comunicacao': parecer.comunicacao,
        'consideracoes_finais': parecer.consideracoes_finais,
        'observacao_coordenador': parecer.observacao_coordenador,
    }

    if request.method == 'POST':
        form = request.POST
        cgn = form.get('aspectos_cognitivos', pAtrib['aspectos_cognitivos'])
        socio = form.get('aspectos_socioemocionais', pAtrib['aspectos_socioemocionais'])
        fis = form.get('aspectos_fisicos_motoras', pAtrib['aspectos_fisicos_motoras'])
        hab = form.get('habilidades', pAtrib['habilidades'])
        contAbordado = form.get('conteudos_abordados', pAtrib['conteudos_abordados'])
        intSocial = form.get('interacao_social', pAtrib['interacao_social'])
        comunica = form.get('comunicacao', pAtrib['comunicacao'])
        consFinais = form.get('consideracoes_finais', pAtrib['consideracoes_finais'])
        obsCoord = form.get('observacao_coordenador', pAtrib['observacao_coordenador'])

        # Atualiza ou cria o ParecerDescritivo
        ParecerDescritivo.objects.update_or_create(
            matricula=pk,
            trimestre__id=trimestre,
            defaults={
                'trimestre': Trimestre.objects.get(pk=trimestre),
                'aspectos_cognitivos': cgn,
                'aspectos_socioemocionais': socio,
                'aspectos_fisicos_motoras': fis,
                'habilidades': hab,
                'conteudos_abordados': contAbordado,
                'interacao_social': intSocial,
                'comunicacao': comunica,
                'consideracoes_finais': consFinais,
                'observacao_coordenador': obsCoord,
            }
        )
        parecer_atualizado = get_object_or_404(ParecerDescritivo, matricula=pk, trimestre__id=trimestre)    
        
        client = Client()
        message_resumo = [
            "Por favor, Com base nas informações\
                  a seguir sobre o aluno, elabore um\
                      parecer descritivo em português, com\
                          no mínimo 500 caracteres que aborde suas\
                              habilidades acadêmicas, comportamento, participação\
                                  em sala de aula e áreas de melhoria. Considere os\
                                      seguintes dados:.",
            ]

        # Adiciona as informações apenas se não estiverem vazias
        if pAtrib.get('aluno'):
            message_resumo.append(f'Nome do Aluno: {pAtrib.get("aluno")}</br>')

        if pAtrib.get('idade'):
            message_resumo.append(f'idade: {pAtrib.get('idade')} anos </br>')
        
        if pAtrib.get('genero'):
            message_resumo.append(f'gênero sexual: {pAtrib.get('geenro')} </br>')

        if pAtrib.get('trimestre'):
            message_resumo.append(f'Trimestre atual: {pAtrib.get("trimestre")} </br>')

        if parecer_atualizado.aspectos_cognitivos:
            message_resumo.append(f'Quanto aos aspectos cognitivos: {parecer_atualizado.aspectos_cognitivos} <br>')

        if parecer_atualizado.aspectos_socioemocionais:
            message_resumo.append(f'Quanto aos aspectos socioemocionais: {parecer_atualizado.aspectos_socioemocionais} <br>')

        if parecer_atualizado.aspectos_fisicos_motoras:
            message_resumo.append(f'Quanto aos aspectos físicos/motoras: {parecer_atualizado.aspectos_fisicos_motoras} <br>')

        if parecer_atualizado.habilidades:
            message_resumo.append(f'Quanto as  habilidades do aluno: {parecer_atualizado.habilidades}<br>')

        if parecer_atualizado.conteudos_abordados:
            message_resumo.append(f'Os conteúdos abordados: {parecer_atualizado.conteudos_abordados} <br>')

        if parecer_atualizado.interacao_social:
            message_resumo.append(f'Quanto a interação social: {parecer_atualizado.interacao_social} <br>')

        if parecer_atualizado.comunicacao:
            message_resumo.append(f'Quanto a comunicação: {parecer_atualizado.comunicacao} <br>')

        if parecer_atualizado.consideracoes_finais:
            message_resumo.append(f'Considerações Finais: {parecer_atualizado.consideracoes_finais} <br>')

        if parecer_atualizado.observacao_coordenador:
            message_resumo.append(f'Observação do Coordenador: {parecer_atualizado.observacao_coordenador} <br>')

        # Gera o resumo usando o G4f
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "\n".join(message_resumo)}]
        )

        resumo = response.choices[0].message.content
        # Atualiza o campo 'resumo'
        ParecerDescritivo.objects.update_or_create(
            matricula=pk,
            trimestre__id=trimestre,
            defaults={'resumo': resumo}
        )

        # ATUALIZA TODOS OS CAMPOS DO TRIMESTRE FINAL COM ORIENTAÇÃO DA IA        
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
        trimestre_id = trimestre    
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

        trimestre = trimestre_id
        parecer_final = ParecerDescritivo.objects.get(matricula=pk, trimestre__final=True)
        texto_orientado = f"Analise o texto sobre o comportamento do aluno {parecer_final.matricula} faça um resumo e em seguida, forneça orientações práticas para o professor em 2º pessoa. Crie uma história fictícia que possa fazer o professor entender como ajudar o aluno. Máximo 500 caracteres"
 
        texto_resumo = f"Com base no seu treinamento, analise o texto e faça um resumo. Dependendo do que foi escrito dê orientações ao profissional. Máximo 500 caracteres"
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

        client_resu = Client()

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
            response = client_resu.chat.completions.create(
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

        nomeTrimestre = Trimestre.objects.get(id=trimestre).numero_nome
        messages.success(request, f"<span class='fs-1'>🤖</span> Parecer do aluno para o {nomeTrimestre} salvo com sucesso! Você já pode conferir a análise realizada pela IA, caso deseje")

    return redirect(reverse_lazy('Gestao_Escolar:criaParecer', kwargs={'turma_id': parecer_atualizado.matricula.turma.id}))


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
 

