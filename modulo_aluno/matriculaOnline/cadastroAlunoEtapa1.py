from django.shortcuts import render, redirect
from gestao_escolar.models import Alunos, AlunoUser
from .matricualOnline_form import MatriculaOnline_etapa1
from django.contrib.auth.models import User, Group
from django.contrib import messages


def cadastro_aluno_etapa1(request, nome, mae):
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
            user = User.objects.get(id=user.id)
        )
        alunoUser.save()        
        print(f'olha ele aqui o id {user_id} - {aluno_id}')
        
        aluno = Group.objects.get(name = 'Aluno')
        user.groups.add(aluno)
        messages.success(request, f"Os dados de acesso de {nome_completo.upper()} foram registrados com sucesso. Login: {login} | Senha: {senha}.")
        messages.info(request, f"{nome_completo.upper()} está agora registrado no sistema. Para completar o processo, é necessário realizar a matrícula em uma das séries disponíveis. Acesse a área de Matrícula Online clicando em 'Login Matrícula' e finalize a matrícula.")
        
        
        #return redirect('Gestao_Escolar:cadastro_aluno_etapa2',  aluno_id=aluno_id)
        #return redirect('Gestao_Escolar:cadastro_aluno_etapa1_exibeSenha',  aluno_id=aluno_id)
        return redirect('Gestao_Escolar:criaAlunoUser', aluno_id=aluno_id, user_id=user_id)

    
    return render(request, 'Escola/matriculaOnline/etapa1.html', {'form':form, 'nomeAluno': nome, 'nomeMae':mae})



from django.shortcuts import render, redirect
from gestao_escolar.models import Alunos, AlunoUser
from django.contrib.auth.models import User
from django.contrib import messages

def criaAlunoUser(request, aluno_id, user_id):
    try:
        # Recupera o Aluno e o User a partir dos IDs passados
        aluno = Alunos.objects.get(id=aluno_id)
        user = User.objects.get(id=user_id)

        # Cria o relacionamento no modelo AlunoUser
        aluno_user = AlunoUser.objects.create(aluno=aluno, user=user)
        aluno_user.save()

        # Adiciona a mensagem de sucesso
        messages.success(request, f"O aluno {aluno.nome_completo} foi vinculado ao usuário {user.username} com sucesso!")

        # Redireciona para outra página ou exibe uma mensagem
        return redirect('Gestao_Escolar:dashboard')  # ou qualquer outra URL desejada

    except Alunos.DoesNotExist:
        messages.error(request, "Aluno não encontrado.")
        return redirect('Gestao_Escolar:cadastro_aluno_etapa1')  # Redireciona para a etapa de cadastro

    except User.DoesNotExist:
        messages.error(request, "Usuário não encontrado.")
        return redirect('Gestao_Escolar:cadastro_aluno_etapa1')  # Redireciona para a etapa de cadastro
