from django.shortcuts import render, redirect
from gestao_escolar.models import Alunos
from .matricualOnline_form import MatriculaOnline_etapa3
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def cadastro_aluno_etapa3(request, aluno_id):
    aluno = Alunos.objects.get(id=aluno_id)
    form = MatriculaOnline_etapa3(request.POST or None, instance=aluno)

    if request.method == 'POST':
        if form.is_valid():  # Check if form is valid before accessing cleaned_data
            # Aqui você pode adicionar mais dados, como telefone, endereço, etc.
            aluno.data_nascimento = form.cleaned_data['data_nascimento']
            aluno.tel_celular_aluno = form.cleaned_data['tel_celular_aluno']
            aluno.sexo = form.cleaned_data['sexo']
            aluno.rua = form.cleaned_data['rua']
            aluno.bairro = form.cleaned_data['bairro']
            aluno.cidade = form.cleaned_data['cidade']
            aluno.cartao_nacional_saude_cns = form.cleaned_data['cartao_nacional_saude_cns']
            aluno.nis = form.cleaned_data['nis']

            aluno.save()
            messages.success(request, f"As informações foram atualizadas com sucesso: RG e CPF. A partir de agora, você atualizarar os dados da Certidão de Nascimento do aluno.")
            return redirect('Gestao_Escolar:cadastro_aluno_etapa3', aluno_id=aluno.id)
        else:
            messages.error(request, "Por favor, corrija os erros no formulário.")

    return render(request, 'Escola/matriculaOnline/etapa3.html', {'aluno': aluno, 'form': form})