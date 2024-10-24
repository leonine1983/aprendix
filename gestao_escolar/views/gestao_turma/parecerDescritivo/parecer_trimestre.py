from django.shortcuts import get_object_or_404, render
from gestao_escolar.models import Matriculas, Trimestre, ParecerDescritivo
from .formsAlunoParecer import AlunoParecerForm

def gestao_turmas_parecer(request, turma_id):
    # Obtém todos os pareceres relacionados à turma
    #parecer = Matriculas.objects.filter(turma=turma_id)
    parecer = ParecerDescritivo.objects.filter(matricula__turma=turma_id)
    #parecer = ParecerDescritivo.objects.filter(matricula__turma=turma_id).select_related('trimestre')


    
    
    # Se você deseja mostrar pareceres individuais, precisará iterar sobre eles.
    # Aqui, por exemplo, assumimos que você quer mostrar todos os pareceres em um formulário.
    
    forms = []
    for item in parecer:
        form = AlunoParecerForm(instance=item)
        forms.append(form)

    print(f'olha os forms {forms}')
   
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
