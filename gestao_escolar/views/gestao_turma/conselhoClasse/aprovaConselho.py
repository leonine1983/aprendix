from ....models import GestaoTurmas
from django.views.generic import View
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

class AprovaConselho(LoginRequiredMixin, View):
    def get (self, request, pk):
        gestao_turma = GestaoTurmas.objects.filter(aluno = pk)
        for g in gestao_turma:
            if g.trimestre.final:
                if g.media_final:
                    if g.media_final < 5:
                        g.conselho_classe = True
                        g.media_anterior_conselho_classe = g.media_final
                        g.media_final = 5.0
                        g.save()

        messages.success(request, f"O aluno {g.aluno} acaba de ser aprovado pelo Conselho de Classe na disciplina {g.grade.disciplina}. A média final dele será 5,0")

        return reverse_lazy('Gestao_Escolar:NotasAluno', g.aluno.turma)


