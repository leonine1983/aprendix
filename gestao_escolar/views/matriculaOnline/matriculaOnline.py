from django.shortcuts import render, redirect
from gestao_escolar.models import Alunos, MatriculasOnline, EscolaMatriculaOnline, SerieOnline, Matriculas
from rh.models import Escola
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .impugarMatricula_form import *


@login_required
def matricular_aluno(request, aluno_id):
    aluno = Alunos.objects.get(id=aluno_id)
    aluno_bairro = aluno.bairro.id
    escola_bairro = EscolaMatriculaOnline.objects.filter(
    Q(ativo = True) &
    Q(escola__related_dadosEscola__bairro__id=aluno_bairro) |
    Q(escola__related_dadosEscola__bairro_atendEscola__id=aluno_bairro)
    )    
   
    return render(request, 'Escola/matriculaOnline/matricular_aluno.html', {'aluno': aluno, "escola":escola_bairro})


# Cria a Pre_matricula do aluno online
@login_required
def finaliza_matricular_aluno(request, aluno_id, serie_id):
    try:
        aluno = Alunos.objects.get(id=aluno_id)
        serie = SerieOnline.objects.get(id=serie_id)
    except Alunos.DoesNotExist:
        messages.error(request, "Aluno não encontrado.")
        return redirect('Gestao_Escolar:matricular_aluno', {'aluno_id':aluno_id})  # Substitua com a URL de erro desejada
    except SerieOnline.DoesNotExist:
        messages.error(request, "Série não encontrada.")
        return redirect('Gestao_Escolar:matricular_aluno', {'aluno_id':aluno_id})  # Substitua com a URL de erro desejada

    # Verifica se o aluno já está matriculado na série
    if MatriculasOnline.objects.filter(aluno=aluno, serie=serie).exists():
        messages.warning(request, "Este aluno já está matriculado nesta série.")
        return redirect('Gestao_Escolar:matricular_aluno', {'aluno_id':aluno_id})  # Substitua com a URL de erro desejada

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
        return redirect('Gestao_Escolar:matricular_aluno', {'aluno_id':aluno_id})  # Substitua com a URL de erro desejada

    # Redirecionamento para a página de confirmação
    return render(
        request,
        'Escola/matriculaOnline/matricula_confirmada.html',
        {'aluno': aluno, 'serie': serie}
    )



@login_required
def matricula_confirma_impugna(request, mat_id):
    try:
        # Retrieve the MatriculasOnline instance using the mat_id
        matricula = MatriculasOnline.objects.get(id=mat_id)
    except MatriculasOnline.DoesNotExist:
        messages.error(request, "Matrícula não encontrada.")
        return redirect('some_error_page')  # Or another page where you handle errors

    # Pass the instance of MatriculasOnline to the form
    form = MatriculasOnlineForm(instance=matricula)

    # You might not need aluno_id if it's just a reference to the same MatriculasOnline object
    aluno_id = matricula.id

    return render(request, 'Escola/inicio.html', {
        'aluno_id': aluno_id,
        'matricula': matricula,
        'form': form,

        'titulo_page': "Análise de Solicitação de Matrícula por Meio da Matrícula Pública (Matrícula Online)",
        'sub_titulo_page': "Utilize os botões abaixo para aprovar a solicitação de matrícula do aluno ou para impugná-la devido à falta de documentos.",
        'btn_bg' : "btn-success",
        'conteudo_page' : 'impugnarConfirmar'
    })




# View para mostrar a confirmação da matrícula
class MatriculasOnlineFormConfirmada(ModelForm):  # Usando ModelForm diretamente
    class Meta:
        model = Matriculas
        fields = ['turma','aluno']


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

@login_required
def matricula_confirmada(request, mat_id):
    # Obtém a matrícula pelo ID (com `get_object_or_404`, se preferir, para simplificar)
    matricula = get_object_or_404(MatriculasOnline, id=mat_id)
    
    # Verifica se o formulário foi enviado via POST
    if request.method == 'POST':
        # Instancia o formulário com os dados POST, passando a instância de MatriculasOnline
        form = MatriculasOnlineFormConfirmada(request.POST, instance=matricula)
        
        # Verifica se o formulário é válido
        if form.is_valid():
            # Salva a matrícula após associar o aluno e os dados da matrícula
            form.save()

            # Após salvar, redireciona para uma página de sucesso ou de confirmação
            return HttpResponseRedirect('/matricula/confirmada/sucesso/')
        else:
            # Se o formulário não for válido, renderiza o template novamente com o formulário
            return render(request, 'matriculas/confirmacao.html', {'form': form, 'matricula': matricula})
    else:
        # Instancia o formulário com a matrícula existente para GET (preenchido com os dados)
        form = MatriculasOnlineFormConfirmada(instance=matricula)

    # Renderiza o template com o formulário para o usuário
    return render(request, 'matriculas/confirmacao.html', {
        'form': form,
        'matricula': matricula,
        'conteudo_page': "Add Series Online",
        'titulo_page': "Seleciona séries para matrícula online",
    })

