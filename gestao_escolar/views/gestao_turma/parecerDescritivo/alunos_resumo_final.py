from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from gestao_escolar.models import ParecerDescritivo, Trimestre
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Atualizar o Resumo Final
@login_required
def alunoGestaoTurmasParecerResumo(request, pk, trimestre):
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
        obsResum = form.get('resumo')

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
                'resumo': obsResum,
            }
        )           

        nomeTrimestre=ParecerDescritivo.objects.get(
            matricula=pk,
            trimestre__id=trimestre)

        messages.success(request, f"<span class='fs-1'>🤖</span> Parecer do aluno {nomeTrimestre.matricula} para o perído {nomeTrimestre.trimestre.numero_nome}, salvo com sucesso! Você já pode conferir a análise realizada pela IA, caso deseje")

    return redirect(reverse_lazy('Gestao_Escolar:criaParecer', kwargs={'turma_id': nomeTrimestre.matricula.turma.id}))