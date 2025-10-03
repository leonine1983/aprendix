from django.shortcuts import render, redirect
from gestao_escolar.models import Alunos, MatriculasOnline, EscolaMatriculaOnline, SerieOnline, Matriculas, Turmas, GestaoTurmas

from rh.models import Escola, Bairro, Ano
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .impugarMatricula_form import *


@login_required
def matricular_aluno(request, aluno_id):
    aluno = Alunos.objects.get(id=aluno_id)
    aluno_bairro = aluno.bairro
    bairro = get_object_or_404(Bairro, nome_bairro = aluno_bairro)
    escola_bairro = EscolaMatriculaOnline.objects.filter(
    Q(ativo = True) &
    Q(escola__related_dadosEscola__bairro__id=bairro.id) |
    Q(escola__related_dadosEscola__bairro_atendEscola__id=bairro.id)
    )    
   
    return render(request, 'Escola/matriculaOnline/matricular_aluno.html', {'aluno': aluno, "escola":escola_bairro})


# Cria a Pre_matricula do aluno online
# Cria a Pre_matricula do aluno online
@login_required
def finaliza_matricular_aluno(request, aluno_id, serie_id):
    try:
        aluno = Alunos.objects.get(id=aluno_id)
        serie = SerieOnline.objects.get(id=serie_id)
    except Alunos.DoesNotExist:
        messages.error(request, "Aluno não encontrado.")
        return redirect('Gestao_Escolar:matricular_aluno', aluno_id=aluno_id)
    except SerieOnline.DoesNotExist:
        messages.error(request, "Série não encontrada.")
        return redirect('Gestao_Escolar:matricular_aluno', aluno_id=aluno_id)

    # Verifica se o aluno já possui matrícula no mesmo ano letivo
    if MatriculasOnline.objects.filter(
        aluno=aluno,
        serie__escola__ano_letivo=serie.escola.ano_letivo
    ).exists():
        messages.warning(request, f"Este aluno já possui uma matrícula no ano letivo de {serie.escola.ano_letivo}.")
        return redirect('Gestao_Escolar:matricular_aluno', aluno_id=aluno_id)

    try:
        # Criação do registro de matrícula
        matricula = MatriculasOnline.objects.create(
            aluno=aluno,
            serie=serie
        )
        messages.success(
            request,
            f"Parabéns! A pré-matrícula do aluno {aluno} na {serie} foi realizada com sucesso! "
            f"Agora, é só esperar a confirmação da escola para que a matrícula seja efetivada. "
            
        )
    except Exception as e:
        messages.error(request, f"Ocorreu um erro ao realizar a matrícula: {e}")
        return redirect('Gestao_Escolar:matricular_aluno', aluno_id=aluno_id)

    # Redirecionamento para a página de confirmação
    return render(
        request,
        'Escola/matriculaOnline/matricula_confirmada.html',
        {'aluno': aluno, 'serie': serie}
    )



from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
@login_required
def matricula_confirma_impugna(request, mat_id):
    matricula = get_object_or_404(MatriculasOnline, id=mat_id)

    if request.method == "POST":
        form = MatriculasOnlineForm(request.POST, instance=matricula)
        if form.is_valid():
            # Marca como impugnada sempre que salvar
            matricula = form.save(commit=False)
            matricula.impugnar = True
            if not matricula.pendecia:  # se não tiver pendência preenchida
                matricula.pendecia = "Matrícula impugnada por falta de documentos."
            matricula.save()

            messages.warning(request, "A matrícula foi marcada como impugnada.")
            return redirect('Gestao_Escolar:matricular_aluno', aluno_id=matricula.id)
        else:
            messages.error(request, "Erro ao salvar a matrícula.")
    else:
        form = MatriculasOnlineForm(instance=matricula)

    return render(request, 'Escola/inicio.html', {
        'aluno_id': matricula.id,
        'matricula': matricula,
        'form': form,
        'titulo_page': "Análise de Solicitação de Matrícula por Meio da Matrícula Pública (Matrícula Online)",
        'sub_titulo_page': "Utilize os botões abaixo para aprovar a solicitação de matrícula do aluno ou para impugná-la devido à falta de documentos.",
        'btn_bg': "btn-success",
        'conteudo_page': 'impugnarConfirmar'
    })




# View para mostrar a confirmação da matrícula
class MatriculasOnlineFormConfirmada(ModelForm):  # Usando ModelForm diretamente
    class Meta:
        model = Matriculas
        fields = ['turma','aluno']       
    
    def __init__(self, *args, **kwargs):
        turma_queryset = kwargs.pop('turma_queryset', None) 
        aluno_query = kwargs.pop('aluno_query', None)
        super().__init__(*args, **kwargs)
        if turma_queryset is not None:
            self.fields['turma'].queryset = turma_queryset 

        if aluno_query is not None:
            self.fields['aluno'].queryset = aluno_query       


from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, get_object_or_404, redirect

@login_required
def matricula_confirmada(request, mat_id):
    # Obtém a matrícula online
    matricula_online = get_object_or_404(MatriculasOnline, id=mat_id)
    
    aluno_queryset = Alunos.objects.filter(id=matricula_online.aluno.id)
    turma_queryset = Turmas.objects.filter(
        serie=matricula_online.serie.serie,
        ano_letivo=matricula_online.serie.escola.ano_letivo       
    )  

    if request.method == 'POST':
        form = MatriculasOnlineFormConfirmada(request.POST, instance=matricula_online)
        
        if form.is_valid():
            # Cria nova instância de Matriculas a partir do form
            matricula_nova = Matriculas.objects.create(
                aluno=form.cleaned_data['aluno'],
                turma=form.cleaned_data['turma']
            )
            print(f' a matriucl : {matricula_nova} {matricula_nova.turma}')
            """
            # Marca a matrícula online como confirmada
            matricula_em_gestaoTurmas =  Matriculas.objects.get(id=matricula_nova.id)
            if matricula_em_gestaoTurmas:
                GestaoTurmas.objects.get_or_create(
                    aluno = matricula_em_gestaoTurmas
                )
                messages.info(request, f"O aluno {matricula_nova} foi inserido em gestao de turmas")

                """
            

            matricula_online.confirma = True
            matricula_online.save()

            return redirect('Gestao_Escolar:GE_Escola_Matricula_create', matricula_nova.turma.id)
        else:
            return render(request, 'Escola/matriculaOnline/matricula_sucesso/sucesso.html', {
                'form': form,
                'matricula': matricula_online
            })
    else:
        form = MatriculasOnlineFormConfirmada(
            instance=matricula_online,
            turma_queryset=turma_queryset,
            aluno_query=aluno_queryset
        )

    return render(request, 'Escola/inicio.html', {
        'form': form,
        'matricula': matricula_online,
        'conteudo_page': "Add Series Online",
        'title_page': "Seleciona séries para matrícula online",
        'titulo_page': "Seleciona séries para matrícula online",
    })
