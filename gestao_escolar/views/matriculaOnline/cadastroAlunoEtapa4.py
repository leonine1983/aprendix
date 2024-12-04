from django.shortcuts import render, redirect
from gestao_escolar.models import Alunos
from django.contrib.auth.decorators import login_required
from .matricualOnline_form import MatriculaOnline_etapa4
from django.contrib import messages


@login_required
def cadastro_aluno_etapa4(request, aluno_id):
    aluno = Alunos.objects.get(id=aluno_id)
    form = MatriculaOnline_etapa4(request.POST or None, instance=aluno)
    if request.method == 'POST':
        if form.is_valid():
            # Aqui você pode adicionar mais dados, como dados de saúde, escolaridade, etc.
            aluno.nome_mae = form.cleaned_data['nome_mae']
            aluno.tel_celular_mae = form.cleaned_data['tel_celular_mae']
            aluno.nome_pai = form.cleaned_data['nome_pai']
            aluno.tel_celular_pai = form.cleaned_data['tel_celular_pai']
            aluno.estado_civil = form.cleaned_data['estado_civil']
            aluno.tipo_certidao = form.cleaned_data['tipo_certidao']
            aluno.numero_certidao = form.cleaned_data['numero_certidao']
            aluno.livro = form.cleaned_data['livro']
            aluno.folha = form.cleaned_data['folha']
            aluno.termo = form.cleaned_data['termo']
            if 'estado_naturalidade' in form.cleaned_data:
                aluno.estado_naturalidade = form.cleaned_data['estado_naturalidade']
            else:
                messages.error(request, "O campo Estado de Naturalidade não foi preenchido.")
            aluno.emissao = form.cleaned_data['emissao']
            aluno.distrito_certidao = form.cleaned_data['distrito_certidao']
            aluno.comarca = form.cleaned_data['comarca']
            aluno.cartorio_uf = form.cleaned_data['cartorio_uf']   

            aluno.save()
            messages.success(request, f"As informações foram atualizadas com sucesso: Certidão de nascimento e filiação. A partir de agora, você atualizarar os dados físicos e biológicos do aluno.")
            return redirect('Gestao_Escolar:cadastro_aluno_etapa5', aluno_id=aluno.id)
    
    
    return render(request, 'Escola/matriculaOnline/etapa4.html', {'aluno': aluno, 'form':form})
