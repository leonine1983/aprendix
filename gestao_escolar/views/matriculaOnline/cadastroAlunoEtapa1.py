from django.shortcuts import render, redirect
from gestao_escolar.models import Alunos, AlunoUser
from .matricualOnline_form import MatriculaOnline_etapa1
from django.contrib.auth.models import User, Group
from django.contrib import messages

from django.core.mail import send_mail
from django.conf import settings

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rh.models import Config_plataforma

def enviaEmail(assunto, template_html, contexto, email_destino):
    """
    Envia um e-mail HTML com template renderizado.
    - assunto: Assunto do e-mail
    - template_html: caminho do template (ex: 'emails/matricula_confirmada.html')
    - contexto: dicionário com dados para o template
    - email_destino: destinatário ou lista de e-mails
    """
    # Renderiza o HTML do template
    html_message = render_to_string(template_html, contexto)

    # Gera uma versão texto puro (para fallback)
    plain_message = strip_tags(html_message)

    # Garante que o destino seja uma lista
    if isinstance(email_destino, str):
        email_destino = [email_destino]

    send_mail(
        subject=assunto,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=email_destino,
        html_message=html_message,
        fail_silently=False,
    )



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
        nome_sistema = Config_plataforma.objects.all().last()
        try:
            assunto = f"Cadastro concluído - {nome_completo}"
            mensagem = (
                f"<p>Olá {first_name.upper()},</p>\n\n"
                f"<p>Seja bem-vindo(a) ao {nome_sistema}! 🎉</p>\n\n"
                f"<p>Seu cadastro foi realizado com sucesso e agora você já pode acessar o sistema para iniciar sua matrícula online.</p>\n\n"
                f"<p>Aqui estão seus dados de acesso:</p>\n"
                f"<ul><li>Usuário: {login}</li>\n"
                f"<li>Senha: {senha}</li></ul>\n\n"
                f"<p>Se tiver qualquer dúvida, fique à vontade para procurar a escola escolhida — eles estarão prontos para te ajudar.</p>\n\n"
                f"<p>Um ótimo início de jornada com o AprendiX!</p>\n\n"
                f"<p>Com carinho,\n Equipe {nome_sistema}</p>"                
            )

            contexto = {
                'aluno': aluno,
                'login':login,
                'senha':senha,
                'mensagem':mensagem,
                'nome_sistema':nome_sistema,
                'dominio': nome_sistema.dominio
            }

            enviaEmail(
                assunto= assunto ,
                template_html='Escola/emails/confirma_cadastro.html',
                contexto=contexto,
                email_destino=aluno.email,
            )  
            messages.success(request, f"E-mail de confirmação enviado para {email}.")
        except Exception as e:
            messages.warning(request, f"Cadastro concluído, mas ocorreu um erro ao enviar o e-mail: {e}")

        # Mensagens no sistema
        messages.success(request, f"Os dados de acesso de {nome_completo.upper()} foram registrados com sucesso. Login: {login} | Senha: {senha}.")
        messages.info(request, f"{nome_completo.upper()} está agora registrado no sistema. Para completar o processo, é necessário realizar a matrícula em uma das séries disponíveis. Acesse a área de Matrícula Online clicando em 'Login Matrícula' e finalize a matrícula.")

        return redirect('Gestao_Escolar:cadastro_aluno_etapa1_exibeSenha', aluno_id=aluno.id)

    return render(request, 'Escola/matriculaOnline/etapa1.html', {'form': form, 'nomeAluno': nome, 'nomeMae': mae})

