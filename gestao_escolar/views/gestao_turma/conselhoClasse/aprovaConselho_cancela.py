from ....models import GestaoTurmas, Matriculas
from django.views.generic import View
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin

class AprovaConselhoCancela(LoginRequiredMixin, View):
    
    def get(self, request, pk):
        aluno = Matriculas.objects.get(pk = pk)
        gestao_turma = GestaoTurmas.objects.filter(aluno=pk)
        for g in gestao_turma:
            if g.trimestre.final:
                g.media_final = g.media_anterior_conselho_classe
                g.aluno.aprovado_conselho = False
                g.save()
                g.aluno.save()
                messages.success(request, f"O aluno {aluno} acaba de ter sua media final restaurada")

        return redirect('Gestao_Escolar:NotasAluno', g.aluno.turma.id)


