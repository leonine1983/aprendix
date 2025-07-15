from django.shortcuts import get_object_or_404, render
from gestao_escolar.models import Matriculas, Trimestre, ParecerDescritivo
from .formsAlunoParecer import AlunoParecerForm

def gestao_turmas_parecer(request, turma_id):
    parecer = ParecerDescritivo.objects.filter(matricula__turma=turma_id)
    #parecer = ParecerDescritivo.objects.filter(matricula__turma=turma_id).select_related('trimestre')
    
    forms = []
    for item in parecer:
        form = AlunoParecerForm(instance=item)
        forms.append(form)
   
    # Obtém as matrículas da turma
    turma = Matriculas.objects.filter(turma=turma_id)
    trimestres = Trimestre.objects.all()

    context = {
        'form': forms,  
        'turma': turma,       
        'trimestres': trimestres,
        'conteudo_page': "Gestão Turmas - Parecer",
    }

    return render(request, 'Escola/inicio.html', context)
