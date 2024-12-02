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
            aluno.CPF = form.cleaned_data['CPF']
            aluno.RG = form.cleaned_data['RG']
            aluno.RG_emissao = form.cleaned_data['orgao_emissor']
            aluno.RG_UF = form.cleaned_data['RG_UF']
            aluno.naturalidade = form.cleaned_data['naturalidade']
            aluno.estado_naturalidade = form.cleaned_data['estado_naturalidade']
            aluno.nacionalidade = form.cleaned_data['nacionalidade']
            aluno.aluno_exterior = form.cleaned_data['aluno_exterior']
            aluno.pais_origem = form.cleaned_data['pais_origem']
            aluno.data_entrada_no_pais = form.cleaned_data['data_entrada_no_pais']
            aluno.documento_estrangeiro = form.cleaned_data['documento_estrangeiro']

            aluno.save()
            messages.success(request, f"As informações foram atualizadas com sucesso: RG e CPF. A partir de agora, você atualizarar os dados da Certidão de Nascimento do aluno.")
            return redirect('Gestao_Escolar:cadastro_aluno_etapa3', aluno_id=aluno.id)
        else:
            messages.error(request, "Por favor, corrija os erros no formulário.")

    return render(request, 'Escola/matriculaOnline/etapa3.html', {'aluno': aluno, 'form': form})