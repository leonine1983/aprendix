from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from gestao_escolar.models import ParecerDescritivo, Trimestre
from django.contrib import messages
from g4f.client import Client

def alunoGestaoTurmasParecer(request, pk, trimestre):
    parecer = ParecerDescritivo.objects.filter(matricula=pk, trimestre=trimestre).first()
    """
    if not parecer:
        # Tratar caso em que não existe parecer
        return HttpResponse("Parecer não encontrado.", status=404)
    """
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
        'aspectos_cognitivos': [''],
        'aspectos_socioemocionais': [],
        'aspectos_fisicos_motoras': [],
        'habilidades': [],
        'conteudos_abordados': [],
        'interacao_social': [],
        'comunicacao': [],
        'consideracoes_finais': [],
        'observacao_coordenador': []
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

    parecer_final = ParecerDescritivo.objects.get(matricula=pk, trimestre__final=True)
    texto_orientado = f"Analise o texto sobre o comportamento do aluno {parecer_final.matricula} faça um resumo e em seguida, forneça orientações práticas para o professor em 2º pessoa. Crie uma história fictícia que possa fazer o professor entender como ajudar o aluno. Máximo 500 caracteres"

    aspectos_cognitivos = f"{texto_orientado}: {infoAll.get('aspectos_cognitivos')}"

    client = Client()

    response_cogn = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": f"{aspectos_cognitivos}\n\nPor favor, forneça as orientações em português."
        }]
    )

    resumo_cogn = response_cogn.choices[0].message.content

    ParecerDescritivo.objects.update_or_create(
        matricula=pk, 
        trimestre__final=True,
        defaults={
            'aspectos_cognitivos': resumo_cogn  # Corrigido
        }
    )

    # Retorna o resultado como JSON
    return JsonResponse({
        'resumo_cognitivo': mark_safe(resumo_cogn),
        # Adicione outros dados que você deseja retornar
    })
