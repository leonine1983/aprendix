from django.shortcuts import render, redirect
from gestao_escolar.models import Alunos, MatriculasOnline
from django.db.models import Q


def matricular_aluno(request, aluno_id):
    aluno = Alunos.objects.get(id=aluno_id)
    if request.method == 'POST':
        # Aqui você pode criar o objeto de matrícula
        matricula = MatriculasOnline.objects.create(
            aluno=aluno,
            serie=request.POST.get('serie'),
            ano_letivo=request.POST.get('ano_letivo'),
            escola=request.POST.get('escola')
        )
        matricula.save()
        return render(request, 'matricula_online/matricula_confirmada.html', {'aluno': aluno})

    return render(request, 'Escola/matriculaOnline/matricular_aluno.html', {'aluno': aluno})
"""

class MatriculasOnline(models.Model):    
    cod_matriculaOline = models.TextField(max_length=200, null=True, default='2025-001')
    aluno = models.ForeignKey(Alunos, related_name='related_matriculaOnline_alunos', on_delete=models.CASCADE)
    serie =  models.ForeignKey(Serie_Escolar, related_name="related_serie_matricula", on_delete=models.CASCADE)
    ano_letivo = models.ForeignKey(AnoLetivo, related_name="related_anoLetivoOnline", on_delete=models.CASCADE)
    matriculaConfirmada = models.BooleanField(default=False)
    escola = models.ForeignKey('rh.Escola', related_name='OnlineMatriculaEscola', on_delete=models.CASCADE)

"""