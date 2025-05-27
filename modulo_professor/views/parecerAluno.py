from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from gestao_escolar.models import ParecerDescritivo, Trimestre, Matriculas
from g4f.client import Client 

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django import forms

from gestao_escolar.models import (
    Trimestre,
    Matriculas
)



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
 
