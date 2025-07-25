# iniciar_registros.py

import os
import django

# Configura o Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sme.settings")  # Substitua pelo nome do seu projeto
django.setup()

from admin_acessos.models import MessageUser, NomeclaturaJanelas
from rh.models import *
from django.contrib.auth.models import User, Group
from datetime import datetime

def iniciar_registros():
    try:
        print("------ Inicializando os registros do Moldulo Admin Acessos ------")
        if not MessageUser.objects.exists():
            for user in User.objects.all():
                MessageUser.objects.get_or_create(
                    destinatario=user,
                    assunto="Olá!",
                    mensagem="Bem-vindo ao nosso sistema!",
                )
            print("Mensagens criadas com sucesso.")

        if not NomeclaturaJanelas.objects.exists():
            NomeclaturaJanelas.objects.get_or_create(
                nome_disciplina='Objetos da Aprendizagem/Disciplinas',
                notas='Notas do Aluno'
            )
            print("Nomeclatura criada com sucesso.")

        group_names = ['Nutricionista', 'Professor', 'Diretor', 'Aluno']
        if not Group.objects.exists():
            for group_name in group_names:
                Group.objects.get_or_create(name=group_name)
            print("Grupos criados com sucesso.")
        print("")
        print("")     
        print("------ Inicializando os registros do Moldulo RH ------")
        if not Config_plataforma.objects.exists():
            Config_plataforma.objects.create(
                nome_sistema='Meu Sistema',
                versao='1.0.0'
                # Adicione outros campos obrigatórios conforme o seu modelo
            )
            print("Configuração de prataforma criados com sucesso.")

        # Cria os registros UF se não existirem
        if not Uf_Unidade_Federativa.objects.exists():
            uf_estados = [
                ('AC', 'Acre'), ('AL', 'Alagoas'), ('AM', 'Amazonas'), ('AP', 'Amapá'),
                ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
                ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MG', 'Minas Gerais'), ('MS', 'Mato Grosso do Sul'),
                ('MT', 'Mato Grosso'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PE', 'Pernambuco'),
                ('PI', 'Piauí'), ('PR', 'Paraná'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
                ('RO', 'Roraima'), ('RR', 'Rondônia'), ('RS', 'Rio Grande do Sul'), ('SC', 'Santa Catarina'),
                ('SE', 'Sergipe'), ('SP', 'São Paulo'), ('TO', 'Tocantins')
            ]
            Uf_Unidade_Federativa.objects.bulk_create(
                [Uf_Unidade_Federativa(sigla=s, estado=e) for s, e in uf_estados]
            )
            print("Estados criados com sucesso.")

        # Cria registros Cidade e Bairro se não existirem
        if not Cidade.objects.exists():
            try:
                uf_unidade_federativa = Uf_Unidade_Federativa.objects.get(sigla='BA')
                Cidade.objects.create(nome_estado=uf_unidade_federativa, nome_cidade='Vera Cruz')   
                print("Cidade criada com sucesso.")

            except Uf_Unidade_Federativa.DoesNotExist:
                print("UF Unidade Federativa de sigla BA não encontrada.")

        if not Bairro.objects.exists():
            try:
                cidade = Cidade.objects.get(nome_cidade='Vera Cruz')
                bairros = [
                    "Aratuba", "Baiacu", "Barra do Gil", "Barra do Pote", "Berlinque",
                    "Cacha Pregos", "Campinas", "Cine", "Conceição", "Coroa", 
                    "Gamboa", "Ilhota", "Juerana", "Mar Grande", "Matarandiba", 
                    "Ponta Grossa", "Porrãozinho"
                ]
                for nome_bairro in sorted(bairros):  # Garantindo ordem alfabética
                    Bairro.objects.create(nome_cidade=cidade, nome_bairro=nome_bairro)
                    print("Bairros criados com sucesso.")

            except Cidade.DoesNotExist:
                print("Cidade com ID 1 não encontrada.")                
        
        if not Prefeitura.objects.exists():
            try:
                cidade = Cidade.objects.get(nome_cidade='Vera Cruz')
                estado = Uf_Unidade_Federativa.objects.get(sigla='BA')
                Prefeitura.objects.create(
                    nome='Prefeitura Municipal de Vera Cruz',
                    instituto='Secretaria Municipal da Educação',
                    cidade=cidade,
                    estado=estado,
                    endereco='Av. Te encontro lá',
                    pessoa_publica='Igor Pinho',
                    brasao = ''
                )
                print("Prefeitura registrada com sucesso.")     
            except Cidade.DoesNotExist:
                print("Cidade com PK 1 não encontrada.")
            except Uf_Unidade_Federativa.DoesNotExist:
                print("UF Unidade Federativa com PK 1 não encontrada.")

        if not Ano.objects.exists():
            try:
                prefeitura = Prefeitura.objects.get(nome='Prefeitura Municipal de Vera Cruz')
                data_in = datetime.strptime('12/03/2025', '%d/%m/%Y').date()
                data_end = datetime.strptime('19/12/2025', '%d/%m/%Y').date()
                Ano.objects.create(
                    prefeitura = prefeitura,
                    ano='2025',
                    data_inicio=data_in,
                    data_fim = data_end)
                print('Ano Letivo criado com sucesso!!!')
            except Prefeitura.DoesNotExist:
                print("A prefeitura selecionada não existe")

        
        if not Profissao.objects.exists():
            nome_descreve = [
                ('Diretor Escolar', 'Profissional encarregado da administração e gestão de uma escola.'),
                ('Vice-Diretor Escolar', 'Profissional que auxilia o diretor escolar na administração e gestão da escola, assumindo suas funções na sua ausência e colaborando nas decisões administrativas e pedagógicas.'),
                ('Coordenador Escolar', 'Profissional que supervisiona as operações e as atividades educacionais de uma escola.'),
                ('Secretária escolar', 'Profissional responsável por tarefas administrativas e organizacionais dentro de uma instituição de ensino.'),
                ('Professor', 'Profissional dedicado à educação e ao ensino, desempenhando um papel fundamental na transmissão de conhecimentos, habilidades e valores para os alunos.'), 
                ('Reserva Técnica', 'Profissional responsável por apoiar a infraestrutura e a logística do ambiente escolar, garantindo que todos os recursos necessários estejam disponíveis para o funcionamento adequado das atividades educacionais.'),
                ('Auxiliar de Classe', 'Colaborador que assiste o professor no dia a dia da sala de aula, ajudando na gestão de alunos e na preparação de materiais, contribuindo para um ambiente de aprendizado mais eficaz e acolhedor.'),
                ('Merendeira', 'Funcionária responsável pela preparação e distribuição das refeições escolares.'),
                ('Técnica em alimentação escolar', 'Profissional especializada em planejar, preparar e supervisionar refeições nutritivas e balanceadas.'),
                ('Porteiro escolar', 'Profissional encarregado de monitorar e controlar o acesso à escola.'),            
                ('Auxiliar Administrativo Escolar', 'Profissional que oferece suporte em atividades administrativas dentro de uma instituição educacional.')
                
            ]

            Profissao.objects.bulk_create(
                [Profissao(nome_profissao=nome, descricao=descricao) for nome, descricao in nome_descreve]
            )
            print('Profissão criado com sucesso!!!')

        # Cria registros de Sexo se não existirem
        if not Sexo.objects.exists():
            Sexo.objects.bulk_create(
                [Sexo(nome=sexo) for sexo in [
                    'Masculino (cisgênero)',
                    'Feminino (cisgênero)',
                    'Homem trans',
                    'Mulher trans',
                    'Travesti',
                    'Não-binário',
                    'Agênero',
                    'Gênero-fluido',
                    'Bigênero',
                    'Demiboy',
                    'Demigirl',
                    'Intersexo',
                    'Outro',
                    'Prefere não informar'
                ]]

            )
            print('Gênero Sexual criado com sucesso!!!')

        

        if not Escola.objects.exists():
            prefeitura = Prefeitura.objects.all().first()
            
            if prefeitura is None:
                print("Nenhuma prefeitura encontrada.")
            else:
                # Definindo as escolas a serem criadas
                escolas = [
                        (prefeitura, "Escola Municipal Geralda Maria"),
                        (prefeitura, "Colégio Municipal de Vera Cruz"),
                        (prefeitura, "Centro de Atendimento Educacional Especializado Dr Nicandro Moreira de Macedo"),
                        (prefeitura, "Centro Municipal de Educação Infantil de Cacha Pregos"),
                        (prefeitura, "Colégio Municipal Telma Régis de Andrade"),
                        (prefeitura, "Colégio Municipal Geralda Maria da Conceição"),
                        (prefeitura, "Colégio Municipal Jarbas Passarinho"),
                        (prefeitura, "Colégio Municipal Luiz Eduardo Magalhães"),
                        (prefeitura, "Colégio Municipal Professora Daulia Angélica de Souza Santos"),
                        (prefeitura, "Creche de Jiribatuba"),
                        (prefeitura, "Creche Escola Municipal Educandário Tio Aurélio"),
                        (prefeitura, "Creche Escola Municipal Elza Galvão"),
                        (prefeitura, "Creche Escola Municipal Professora Nice Maria Vinagre de Oliveira"),
                        (prefeitura, "Creche Escola Municipal Simone Trigano"),
                        (prefeitura, "Creche Escola Municipal Vovó Nida"),
                        (prefeitura, "Creche Escola Municipal Vovô Nizio"),
                        (prefeitura, "Escola Clementino Lima"),
                        (prefeitura, "Escola Comunitária Aquilino dos Santos"),
                        (prefeitura, "Escola Dr José Eugênio Mendes Figueiredo"),
                        (prefeitura, "Escola Ivandite Pires Miranda Costa"),
                        (prefeitura, "Escola Major Everaldo Calazans de Almeida"),
                        (prefeitura, "Escola Manoel Januário de Lima"),
                        (prefeitura, "Escola Municipal Presidente Emílio Garrastazu Médici"),
                        (prefeitura, "Escola Municipal Almiro Antunes de Brito"),
                        (prefeitura, "Escola Municipal Antônio Hermenegildo de Sena Pereira"),
                        (prefeitura, "Escola Municipal Argérico Rocha Borges"),
                        (prefeitura, "Escola Municipal Aureliano de Azevedo Monteiro"),
                        (prefeitura, "Escola Municipal Braz Felisberto de Santana"),
                        (prefeitura, "Escola Municipal de Ponta Grossa"),
                        (prefeitura, "Escola Municipal Gaudêncio Acelino Marques"),
                        (prefeitura, "Escola Municipal Gezilda Alves de Souza"),
                        (prefeitura, "Escola Municipal Guilherme Franco Guimarães"),
                        (prefeitura, "Escola Municipal Hilton Rodrigues"),
                        (prefeitura, "Escola Municipal João José de Macedo"),
                        (prefeitura, "Escola Municipal Joaquim Barreto de Araújo"),
                        (prefeitura, "Escola Municipal Juvenal Galvão"),
                        (prefeitura, "Escola Municipal Margarida Moreira"),
                        (prefeitura, "Escola Municipal Nova Divineia"),
                        (prefeitura, "Escola Municipal Olga Seabra"),
                        (prefeitura, "Escola Municipal Padre Ignácio Alves Pereira"),
                        (prefeitura, "Escola Municipal Professor Jorge Calmon"),
                        (prefeitura, "Escola Municipal Raimundo Afonso Borges"),
                        (prefeitura, "Escola Municipal Turma da Mônica"),
                        (prefeitura, "Escola Narciso Francisco de Pinho"),
                        (prefeitura, "Escola Sede Social do Riachinho"),
                        (prefeitura, "Escola Voluntárias Sociais da Bahia"),
                        (prefeitura, "Ginásio Municipal Estelita Eusébia Santiago dos Santos")
                    ]

                
                # Criar as escolas
                escolas_criadas = Escola.objects.bulk_create(
                    [Escola(prefeitura=p, nome_escola=n) for p, n in escolas]
                )
                print(f"Escolas criadas: {[escola.nome_escola for escola in escolas_criadas]}")

                # Criar um único registro de Escola_admin para cada Escola, garantindo um relacionamento um-para-um
                for escola in escolas_criadas:
                    if not Escola_admin.objects.filter(nome=escola).exists():
                        # Criar o registro de Escola_admin para a escola
                        Escola_admin.objects.create(nome=escola)
                        print(f"Escola_admin criado para: {escola.nome_escola}")
                    else:
                        print(f"Já existe um Escola_admin para: {escola.nome_escola}")

            print(f"Todos registros criados com sucesso")







        














    except Exception as e:
        print(f"Erro ao adicionar registros: {e}")

if __name__ == '__main__':
    iniciar_registros()
