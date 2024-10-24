
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from gestao_escolar.models import ParecerDescritivo, Trimestre
from django.contrib import messages
from g4f.client import Client

def alunoGestaoTurmasParecer(request, pk, trimestre):
    parecer = ParecerDescritivo.objects.filter(matricula=pk, trimestre=trimestre)
    print(f'olha o parecer {parecer}')
    #parecer = get_object_or_404(ParecerDescritivo, matricula=pk, trimestre__id=trimestre)    

    if request.method == 'POST':
        form = request.POST
        cgn = form.get('aspectos_cognitivos')
        socio = form.get('aspectos_socioemocionais')
        fis = form.get('aspectos_fisicos_motoras')
        hab = form.get('habilidades')
        contAbordado = form.get('conteudos_abordados')
        intSocial = form.get('interacao_social')
        comunica = form.get('comunicacao')
        consFinais = form.get('consideracoes_finais')
        obsCoord = form.get('observacao_coordenador')

        # Atualiza ou cria o ParecerDescritivo
        ParecerDescritivo.objects.update_or_create(
            matricula=pk,
            trimestre__id=trimestre,
            defaults={
                'trimestre' : Trimestre.objects.get(pk=trimestre),
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
        message_resumo = []

        # Coleta as informações para gerar o resumo
        
        message_resumo.append(f'Aspectos Cognitivos: {parecer_atualizado.aspectos_cognitivos}')
    
        message_resumo.append(f'Aspectos Socioemocionais: {parecer_atualizado.aspectos_socioemocionais}')
    
        message_resumo.append(f'Aspectos Físicos/Motoras: {parecer_atualizado.aspectos_fisicos_motoras}')
    
        message_resumo.append(f'Habilidades: {parecer_atualizado.habilidades}')
    
        message_resumo.append(f'Conteúdos Abordados: {parecer_atualizado.conteudos_abordados}')
    
        message_resumo.append(f'Interação Social: {parecer_atualizado.interacao_social}')
    
        message_resumo.append(f'Comunicação: {parecer_atualizado.comunicacao}')
    
        message_resumo.append(f'Considerações Finais: {parecer_atualizado.consideracoes_finais}')
    
        message_resumo.append(f'Observação do Coordenador: {parecer_atualizado.observacao_coordenador}')

        # Gera o resumo usando o G4f
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "\n".join(message_resumo)}]
        )

        resumo = response.choices[0].message.content  # Acessa o conteúdo corretamente

        # Atualiza o campo 'resumo'
        ParecerDescritivo.objects.update_or_create(
            matricula=pk,
            trimestre__id=trimestre,
            defaults={'resumo': resumo}
        )


        messages.success(request, "Parecer do aluno salvo com sucesso")
    
    return redirect(reverse_lazy('Gestao_Escolar:criaParecer', kwargs={'turma_id': parecer_atualizado.matricula.turma.id}))

