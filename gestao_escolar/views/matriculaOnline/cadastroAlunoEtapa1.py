from django.shortcuts import render, redirect
from gestao_escolar.models import Alunos, AlunoUser
from .matricualOnline_form import MatriculaOnline_etapa1
from django.contrib.auth.models import User, Group
from django.contrib import messages
"""

def cadastro_aluno_etapa1(request, nome, mae, cpf):
    
    form = MatriculaOnline_etapa1(request.POST or None)
   

    if request.method == 'POST' and form.is_valid(): 
        nome_completo = nome
        nome_mae = mae
        login = form.cleaned_data.get('login_aluno')
        senha = form.cleaned_data.get('senha')
        email = form.cleaned_data.get('email')
        
        aluno = Alunos.objects.create(
            nome_completo=nome_completo,
            nome_mae=nome_mae,
            CPF_mae = cpf,
            login_aluno = login,
            senha = senha,
            email  = email
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
        user_id = user.id       
        alunoUser = AlunoUser.objects.create(
            aluno = Alunos.objects.get(id=aluno_id),
            user = User.objects.get(id=user_id)
        )
        alunoUser.save()    
        aluno = Group.objects.get(name = 'Aluno')
        user.groups.add(aluno)
        messages.success(request, f"Os dados de acesso de {nome_completo.upper()} foram registrados com sucesso. Login: {login} | Senha: {senha}.")
        messages.info(request, f"{nome_completo.upper()} está agora registrado no sistema. Para completar o processo, é necessário realizar a matrícula em uma das séries disponíveis. Acesse a área de Matrícula Online clicando em 'Login Matrícula' e finalize a matrícula.")
                
        return redirect('Gestao_Escolar:cadastro_aluno_etapa1_exibeSenha',  aluno_id=aluno_id)
    
    return render(request, 'Escola/matriculaOnline/etapa1.html', {'form':form, 'nomeAluno': nome, 'nomeMae':mae})

    """

from django.shortcuts import render, redirect
from gestao_escolar.models import Alunos, AlunoUser
from .matricualOnline_form import MatriculaOnline_etapa1
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings


def cadastro_aluno_etapa1(request, nome, mae, cpf):
    form = MatriculaOnline_etapa1(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        nome_completo = nome
        nome_mae = mae
        login = form.cleaned_data.get('login_aluno')
        senha = form.cleaned_data.get('senha')
        email = form.cleaned_data.get('email')

        # Cria o registro do aluno
        aluno = Alunos.objects.create(
            nome_completo=nome_completo,
            nome_mae=nome_mae,
            CPF_mae=cpf,
            login_aluno=login,
            senha=senha,
            email=email
        )
        aluno.save()

        # Cria o usuário vinculado
        parteNome = nome_completo.split()
        first_name = parteNome[0]
        last_name = " ".join(parteNome[1:]) if len(parteNome) > 1 else ""

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=login,
            password=senha,
            email=email
        )
        user.save()

        # Relaciona o aluno com o usuário
        AlunoUser.objects.create(aluno=aluno, user=user)

        # Adiciona ao grupo "Aluno"
        grupo_aluno = Group.objects.get(name='Aluno')
        user.groups.add(grupo_aluno)

        # Envio do e-mail de confirmação
        try:
            assunto = f"Cadastro concluído - {nome_completo}"
            mensagem = (
                f"Olá {first_name},\n\n"
                f"Seu cadastro no sistema AprendiX foi realizado com sucesso!\n\n"
                f"Aqui estão seus dados de acesso:\n"
                f"Usuário: {login}\n"
                f"Senha: {senha}\n\n"
                f"Acesse o portal e conclua sua matrícula.\n\n"
                f"Atenciosamente,\nEquipe AprendiX"
            )
            send_mail(
                assunto,
                mensagem,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, f"E-mail de confirmação enviado para {email}.")
        except Exception as e:
            messages.warning(request, f"Cadastro concluído, mas ocorreu um erro ao enviar o e-mail: {e}")

        # Mensagens no sistema
        messages.success(request, f"Os dados de acesso de {nome_completo.upper()} foram registrados com sucesso. Login: {login} | Senha: {senha}.")
        messages.info(request, f"{nome_completo.upper()} está agora registrado no sistema. Para completar o processo, é necessário realizar a matrícula em uma das séries disponíveis. Acesse a área de Matrícula Online clicando em 'Login Matrícula' e finalize a matrícula.")

        return redirect('Gestao_Escolar:cadastro_aluno_etapa1_exibeSenha', aluno_id=aluno.id)

    return render(request, 'Escola/matriculaOnline/etapa1.html', {'form': form, 'nomeAluno': nome, 'nomeMae': mae})

