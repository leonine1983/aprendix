from ....models import GestaoTurmas, Matriculas, Turmas
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
                g.aluno.reprovado_conselho = False
                g.save()
                g.aluno.save()
                messages.success(request, f"O aluno {aluno} acaba de ter sua media final restaurada")

        return redirect('Gestao_Escolar:NotasAluno', g.aluno.turma.id)
    
    
class ReprovaConselho(LoginRequiredMixin, View):
    
    def get(self, request, pk):
        aluno = Matriculas.objects.get(pk = pk)
        gestao_turma = GestaoTurmas.objects.filter(aluno=pk)
        for g in gestao_turma:
            if g.trimestre.final:
                g.media_final = g.media_anterior_conselho_classe
                g.aluno.aprovado_conselho = False
                g.aluno.reprovado_conselho = True
                g.save()
                g.aluno.save()
                messages.warning(request, f"O aluno {aluno} acaba de ser reprovado no conselho de classe")

        return redirect('Gestao_Escolar:NotasAluno', g.aluno.turma.id)
    

class ConcluirTurmas(LoginRequiredMixin, View):
    
    def get(self, request, pk):
        turmas = Turmas.objects.get(pk = pk)
        alunos = Matriculas.objects.filter(turma = pk)
        aluno_concluido = []
        aluno_n_concluido = []
        for a in alunos:
            if a.aprovado or  a.aprovado_conselho or a.aprovado_recupera  or a.reprovado_conselho or a.gestao_turmas_related.last().reprovado_faltas:
                aluno_concluido.append(a)
            else:
                aluno_n_concluido.append(a)

        if aluno_concluido:
            messages.success(self.request, "Turma concluída com sucesso. A partir deste momento, não será mais possível realizar alterações.")
        else:
            nomes = aluno_n_concluido
            messages.warning(
                self.request,
                f"Não foi possível concluir a turma. Os seguintes alunos ainda não têm resultado final registrado: {nomes}. "
                "Retorne à Gestão de Turmas, na opção Notas, e defina se cada aluno foi aprovado ou reprovado."
            )
            
           

        return redirect('Gestao_Escolar:apuracaoSelec', turmas.id)




