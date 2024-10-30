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

        # Crie resumos para cada campo do model Parecer descritivo no trimestre final
        parecer_all = ParecerDescritivo.objects.filter(matricula=pk)
        todos_obs = []
        for p_all in parecer_all:
            if not p_all.trimestre.final:
                todos_obs.append(
                    {
                    'trimestre': p_all.trimestre,
                    'aspectos_cognitivos': p_all.aspectos_cognitivos,
                    'aspectos_socioemocionais': p_all.aspectos_socioemocionais,
                    'aspectos_fisicos_motoras': p_all.aspectos_fisicos_motoras,
                    'habilidades': p_all.habilidades,
                    'conteudos_abordados': p_all.conteudos_abordados,
                    'interacao_social': p_all.interacao_social,
                    'comunicacao': p_all.comunicacao,
                    'consideracoes_finais': p_all.consideracoes_finais,
                    'observacao_coordenador': p_all.observacao_coordenador,
                }
                )  
            if p_all.trimestre.final:                 
                ParecerDescritivo.objects.update_or_create( 
                    trimestre = Trimestre.objects.get(final=True),
                    aspectos_cognitivos = todos_obs['aspectos_cognitivos'],
                    aspectos_socioemocionais = todos_obs['aspectos_socioemocionais'],
                    aspectos_fisicos_motoras = todos_obs['aspectos_fisicos_motoras'],
                    habilidades = todos_obs['habilidades'],
                    conteudos_abordados = todos_obs['conteudos_abordados'],
                    interacao_social = todos_obs['interacao_social'],
                    comunicacao = todos_obs['comunicacao'],
                    consideracoes_finais = todos_obs['consideracoes_finais'],
                    observacao_coordenador = todos_obs['observacao_coordenador'],
                )
                messages.success(request, "Resumo por parâmetro criado com sucesso!")





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

        messages.success(request, "Parecer do aluno salvo com sucesso")

    return redirect(reverse_lazy('Gestao_Escolar:criaParecer', kwargs={'turma_id': parecer_atualizado.matricula.turma.id}))
