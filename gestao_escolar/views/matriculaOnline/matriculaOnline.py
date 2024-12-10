from django.shortcuts import render, redirect
from gestao_escolar.models import Alunos, MatriculasOnline, EscolaMatriculaOnline, SerieOnline
from rh.models import Escola
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def matricular_aluno(request, aluno_id):
    aluno = Alunos.objects.get(id=aluno_id)
    aluno_bairro = aluno.bairro.id
    escola_bairro = EscolaMatriculaOnline.objects.filter(
    Q(escola__related_dadosEscola__bairro__id=aluno_bairro) |
    Q(escola__related_dadosEscola__bairro_atendEscola__id=aluno_bairro)
    )    
   
    return render(request, 'Escola/matriculaOnline/matricular_aluno.html', {'aluno': aluno, "escola":escola_bairro})



@login_required
def finaliza_matricular_aluno(request, aluno_id, serie_id):
    try:
        aluno = Alunos.objects.get(id=aluno_id)
        serie = SerieOnline.objects.get(id=serie_id)
    except Alunos.DoesNotExist:
        messages.error(request, "Aluno não encontrado.")
        return redirect('alguma_rota')  # Substitua com a URL de erro desejada
    except SerieOnline.DoesNotExist:
        messages.error(request, "Série não encontrada.")
        return redirect('alguma_rota')  # Substitua com a URL de erro desejada

    # Verifica se o aluno já está matriculado na série
    if MatriculasOnline.objects.filter(aluno=aluno, serie=serie).exists():
        messages.warning(request, "Este aluno já está matriculado nesta série.")
        return redirect('alguma_rota')  # Substitua com a URL de erro desejada

    try:
        # Criação do registro de matrícula
        matricula = MatriculasOnline.objects.create(
            aluno=aluno,
            serie=serie
        )
        messages.success(
            request,
            f"Parabéns! A pré-matrícula do aluno {aluno} na {serie} foi realizada com sucesso! "
            f"Agora, é só esperar a confirmação da escola para que a matrícula seja efetivada, "
            f"e o aluno possa começar a sua jornada no ano letivo de {serie.escola.ano_letivo}, "
            f"na incrível {serie.escola.escola}. Vamos juntos rumo ao sucesso acadêmico!"
        )
    except Exception as e:
        messages.error(request, f"Ocorreu um erro ao realizar a matrícula: {e}")
        return redirect('alguma_rota')  # Substitua com a URL de erro desejada

    # Redirecionamento para a página de confirmação
    return render(
        request,
        'Escola/matriculaOnline/matricula_confirmada.html',
        {'aluno': aluno, 'serie': serie}
    )


# View para mostrar a confirmação da matrícula
@login_required
def matricula_confirmada(request, aluno_id, serie_id):
    try:
        matricula = MatriculasOnline.objects.get(aluno__id=aluno_id, serie__id=serie_id)
    except MatriculasOnline.DoesNotExist:
        messages.error(request, "Matrícula não encontrada.")
        return redirect('alguma_rota')  # Substitua com a URL de erro desejada

    return render(
        request,
        'Escola/matriculaOnline/matricula_confirmada.html',
        {'matricula': matricula}
    )