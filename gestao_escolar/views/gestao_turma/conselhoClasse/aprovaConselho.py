from ....models import GestaoTurmas, Matriculas
from django.views.generic import View
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin

class AprovaConselho(LoginRequiredMixin, View):
    
    def get(self, request, pk):
        aluno = Matriculas.objects.get(pk = pk)
        gestao_turma = GestaoTurmas.objects.filter(aluno=pk)
        for g in gestao_turma:
            if g.trimestre.final:
                if g.media_final and g.media_final < 5:
                    g.conselho_classe = True
                    g.media_anterior_conselho_classe = g.media_final
                    g.media_final = 5.0
                    g.save()

            if g.media_final == 5.0:  # Garantindo que a mensagem é enviada após a aprovação
                aluno.aprovado_conselho = True
                aluno.save()
                messages.success(request, f"O aluno {g.aluno} acaba de ser aprovado pelo Conselho de Classe na disciplina {g.grade.disciplina}. A média final dele será 5,0")

        return redirect('Gestao_Escolar:NotasAluno', g.aluno.turma.id)


