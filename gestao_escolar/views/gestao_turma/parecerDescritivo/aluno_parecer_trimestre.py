# views.py
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from gestao_escolar.models import  ParecerDescritivo
from django.contrib import messages



def alunoGestaoTurmasParecer(request, pk):
    parecer = get_object_or_404(ParecerDescritivo, matricula=pk)
    turma_id = parecer.matricula.turma.id
    if request.method == 'POST':
        form = request.POST
        cgn = form.get('aspectos_cognitivos')
        socio = form.get('aspectos_socioemocionais')
        fis = form.get('aspectos_fisicos_motoras')
        hab= form.get('habilidades')
        contAbordado= form.get('conteudos_abordados')
        intSocial= form.get('interacao_social')
        comunica= form.get('comunicacao')
        comunica= form.get('comunicacao')
        consFinais= form.get('consideracoes_finais')
        obsCoord= form.get('observacao_coordenador')

        ParecerDescritivo.objects.update_or_create(
            matricula = pk,
            defaults={
            'aspectos_cognitivos' : cgn,
            'aspectos_socioemocionais' : socio,
            'aspectos_fisicos_motoras' : fis,
            'habilidades' : hab,
            'conteudos_abordados' : contAbordado,
            'interacao_social' : intSocial,
            'comunicacao' : comunica,
            'consideracoes_finais' : consFinais,
            'observacao_coordenador' : obsCoord
            }
        ) 
    messages.success(request, "Parecer do aluno salvo com sucesso")  
    return redirect(reverse_lazy('Gestao_Escolar:criaParecer', kwargs={'turma_id':turma_id} )) 
        

       
 