from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from gestao_escolar.models import ParecerDescritivo, Trimestre
from django.contrib import messages
from g4f.client import Client

def alunoGestaoTurmasParecer(request, pk, trimestre):
    parecer = ParecerDescritivo.objects.filter(matricula=pk, trimestre=trimestre).first()  
    pAtrib = {
        'aluno': parecer.matricula,
        'idade': parecer.matricula.aluno.idade,
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
        print(f"sera que é aqui o erro ANTES : {trimestre} ----- {parecer}")  

        
        # ATUALIZA TODOS OS CAMPOS DO TRIMESTRE FINAL COM ORIENTAÇÃO DA IA
        from django.utils.safestring import mark_safe
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
        print(f"sera que é aqui o erro DEPOIS: {trimestre} ----- {parecer}")  
       

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

        print(f"sera que é aqui o erro  BEM DEPOIS:{trimestre_id} ------- {trimestre} ----- {parecer}")  
        parecer_final = ParecerDescritivo.objects.get(matricula=pk, trimestre__final=True)
        texto_orientado = f"Analise o texto sobre o comportamento do aluno {parecer_final.matricula} faça um resumo e em seguida, forneça orientações práticas para o professor em 2º pessoa. Crie uma história fictícia que possa fazer o professor entender como ajudar o aluno. Máximo 500 caracteres"
        texto_resumo = f"Analise o texto e faça um resumo. Dependendo do que foi escrito dê orientações ao profissional. Máximo 500 caracteres"

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

        nomeTrimestre = Trimestre.objects.get(id=trimestre).numero_nome
        messages.success(request, f"<span class='fs-1'>🤖</span> Parecer do aluno para o {nomeTrimestre} salvo com sucesso! Você já pode conferir a análise realizada pela IA, caso deseje")

    return redirect(reverse_lazy('Gestao_Escolar:criaParecer', kwargs={'turma_id': parecer_atualizado.matricula.turma.id}))



from g4f.client import Client
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe

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
    texto_resumo = f"Analise o texto e faça um resumo. Dependendo do que foi escrito dê orientações ao profissional. Máximo 500 caracteres"

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
 