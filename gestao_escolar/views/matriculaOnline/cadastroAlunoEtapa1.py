from django.shortcuts import render, redirect
from gestao_escolar.models import Alunos
from .matricualOnline_form import Aluno_documento_form
from django.contrib.auth.models import User, Group
from django.contrib import messages


def cadastro_aluno_etapa1(request, nome, mae):
    form = Aluno_documento_form(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        nome_completo = nome
        nome_mae = mae
        data_nascimento = request.POST.get('data_nascimento')
        sexo = request.POST.get('sexo')
        
        aluno = Alunos.objects.create(
            nome_completo=nome_completo,
            nome_mae=nome_mae,
            data_nascimento=data_nascimento,
            sexo_id=sexo
        )
        aluno.save()
        aluno_id = aluno.id
        login = form.cleaned_data.get('login_aluno')
        senha = form.cleaned_data.get('senha')
        email = form.cleaned_data.get('email')

        parteNome = nome_completo.split()
        first_name = parteNome[0]
        last_name = "".join(parteNome[1:])

        user = User.objects.create_user(
            first_name = first_name,
            last_name = last_name,
            username= login,
            password= senha,
            email=email
        )
        user.save()
        aluno = Group.objects.get(name = 'Aluno')
        user.groups.add(aluno)
        messages.success(request, f"Os dados de acesso e o endereço de {nome_completo.upper()} foram registrados com sucesso. Login: {login} | Senha: {senha}.")
        messages.info(request, f"{nome_completo.upper()} está agora registrado no sistema. Para completar o processo, é necessário realizar a matrícula em uma das séries disponíveis. Acesse a área de Matrícula Online clicando em 'Login Matrícula' e finalize a matrícula.")
        """
        
        
        print(f"login: {login} e senha {senha}")        
        return redirect('Gestao_Escolar:pesquisar_aluno')"""
        return redirect('Gestao_Escolar:cadastro_aluno_etapa2',  aluno_id=aluno_id)
    
    return render(request, 'Escola/matriculaOnline/etapa1.html', {'form':form, 'nomeAluno': nome, 'nomeMae':mae})

