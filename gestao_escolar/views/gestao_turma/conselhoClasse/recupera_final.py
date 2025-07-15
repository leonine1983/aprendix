from ....models import GestaoTurmas
from django.views.generic import View
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin

class AprovaConselho(LoginRequiredMixin, View):

    """
    class GestaoTurmas(models.Model):
    aluno = models.ForeignKey(Matriculas, related_name='gestao_turmas_related', null=True, on_delete=models.CASCADE)
    grade = models.ForeignKey(TurmaDisciplina, null=True, on_delete=models.CASCADE)
    trimestre = models.ForeignKey(Trimestre, related_name='trimestre_related_turma', null=True, on_delete=models.CASCADE)
    notas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    faltas = models.IntegerField(null=True, blank=True)
    profissional_resp = models.CharField(max_length=40, null=True)
    data_hora_mod = models.DateTimeField(null=True)

    faltas_total = models.IntegerField(null=True, blank=True)
    recuperacao_final = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    """
    
    def get(self, request, pk):
        gestao_turma = GestaoTurmas.objects.filter(aluno=pk)
        for g in gestao_turma:
            if g.trimestre.final:
                if g.media_final and g.media_final < 5:
                    g.conselho_classe = True
                    g.media_anterior_conselho_classe = g.media_final
                    g.media_final = 5.0
                    g.save()

            if g.media_final == 5.0:  # Garantindo que a mensagem é enviada após a aprovação
                messages.success(request, f"O aluno {g.aluno} acaba de ser aprovado pelo Conselho de Classe na disciplina {g.grade.disciplina}. A média final dele será 5,0")

        return redirect('Gestao_Escolar:NotasAluno', g.aluno.turma.id)


