# iniciar_registros.py

import os
import django

# Configura o Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sme.settings")  # Substitua pelo nome do seu projeto
django.setup()

from admin_acessos.models import MessageUser, NomeclaturaJanelas
from rh.models import *
from gestao_escolar.models import *
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
                    (prefeitura, "Escola Municipal Geralda Maria", True),
                    (prefeitura, "Colégio Municipal de Vera Cruz", True),
                    (prefeitura, "Centro de Atendimento Educacional Especializado Dr Nicandro Moreira de Macedo", False),
                    (prefeitura, "Centro Municipal de Educação Infantil de Cacha Pregos", False),
                    (prefeitura, "Colégio Municipal Telma Régis de Andrade", True),
                    (prefeitura, "Colégio Municipal Geralda Maria da Conceição", True),
                    (prefeitura, "Colégio Municipal Jarbas Passarinho", False),
                    (prefeitura, "Colégio Municipal Luiz Eduardo Magalhães", True),
                    (prefeitura, "Colégio Municipal Professora Daulia Angélica de Souza Santos", True),
                    (prefeitura, "Creche de Jiribatuba", False),
                    (prefeitura, "Creche Escola Municipal Educandário Tio Aurélio", False),
                    (prefeitura, "Creche Escola Municipal Elza Galvão", False),
                    (prefeitura, "Creche Escola Municipal Professora Nice Maria Vinagre de Oliveira", False),
                    (prefeitura, "Creche Escola Municipal Simone Trigano", False),
                    (prefeitura, "Creche Escola Municipal Vovó Nida", False),
                    (prefeitura, "Creche Escola Municipal Vovô Nizio", False),
                    (prefeitura, "Escola Clementino Lima", False),
                    (prefeitura, "Escola Comunitária Aquilino dos Santos", False),
                    (prefeitura, "Escola Dr José Eugênio Mendes Figueiredo", False),
                    (prefeitura, "Escola Ivandite Pires Miranda Costa", False),
                    (prefeitura, "Escola Major Everaldo Calazans de Almeida", False),
                    (prefeitura, "Escola Manoel Januário de Lima", False),
                    (prefeitura, "Escola Municipal Presidente Emílio Garrastazu Médici", False),
                    (prefeitura, "Escola Municipal Almiro Antunes de Brito", False),
                    (prefeitura, "Escola Municipal Antônio Hermenegildo de Sena Pereira", False),
                    (prefeitura, "Escola Municipal Argérico Rocha Borges", False),
                    (prefeitura, "Escola Municipal Aureliano de Azevedo Monteiro", False),
                    (prefeitura, "Escola Municipal Braz Felisberto de Santana", False),
                    (prefeitura, "Escola Municipal de Ponta Grossa", False),
                    (prefeitura, "Escola Municipal Gaudêncio Acelino Marques", False),
                    (prefeitura, "Escola Municipal Gezilda Alves de Souza", False),
                    (prefeitura, "Escola Municipal Guilherme Franco Guimarães", False),
                    (prefeitura, "Escola Municipal Hilton Rodrigues", False),
                    (prefeitura, "Escola Municipal João José de Macedo", True),
                    (prefeitura, "Escola Municipal Joaquim Barreto de Araújo", False),
                    (prefeitura, "Escola Municipal Juvenal Galvão", False),
                    (prefeitura, "Escola Municipal Margarida Moreira", False),
                    (prefeitura, "Escola Municipal Nova Divineia", False),
                    (prefeitura, "Escola Municipal Olga Seabra", False),
                    (prefeitura, "Escola Municipal Padre Ignácio Alves Pereira", False),
                    (prefeitura, "Escola Municipal Professor Jorge Calmon", False),
                    (prefeitura, "Escola Municipal Raimundo Afonso Borges", False),
                    (prefeitura, "Escola Municipal Turma da Mônica", False),
                    (prefeitura, "Escola Narciso Francisco de Pinho", False),
                    (prefeitura, "Escola Sede Social do Riachinho", False),
                    (prefeitura, "Escola Voluntárias Sociais da Bahia", False),
                    (prefeitura, "Ginásio Municipal Estelita Eusébia Santiago dos Santos", True)
                ]

                
                # Criar as escolas
                escolas_criadas = Escola.objects.bulk_create(
                    [Escola(prefeitura=p, nome_escola=n, fund2 = t ) for p, n, t in escolas]
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
        

        print("------ Inicializando os registros do Moldulo Gestão Escolar ------")

        if not Cargo.objects.exists():
            cargos = [
                'Diretor', 'Vice-Diretor', 'Coordenador', 'Professor', 'Auxiliar-Administrativo-I',
                'Auxiliar-Administrativo-II', 'Tecnico-em-Multimeitos-Didáticos', 'Tecnico-em-Merenda-Escolar',
                'Auxiliar-de-Classe', 'Servente-de-limpeza', 'Monitor-de-Informática', 'Merendeira',
                'Porteiro', 'Estagiário'
            ]
            Cargo.objects.bulk_create([Cargo(nome=n) for n in cargos])
            print('Cargos criados com sucesso!!!')

        # Cria os registros Etnia se não existirem
        if not Etnia.objects.exists():
            etnias = ['Branca', 'Negra', 'Parda', 'Amarela', 'Indigena', 'Não declarado']
            Etnia.objects.bulk_create([Etnia(nome=etnia) for etnia in etnias])
            print('Etnias criados com sucesso!!!')

        # Cria os registros Nacionalidade se não existirem
        if not Nacionalidade.objects.exists():
            nacionalidades = ['Brasileira', 'Brasileiro nascido no exterior', 'Mexicano']
            Nacionalidade.objects.bulk_create([Nacionalidade(nome=nacionalidade) for nacionalidade in nacionalidades])
            print('Nacionalides criados com sucesso!!!')

        # Cria os registros Pais_origem se não existirem
        if not Pais_origem.objects.exists():
            paises = ['Brasil', 'Japão', 'México']
            Pais_origem.objects.bulk_create([Pais_origem(nome=pais) for pais in paises])
            print('País de origem criado com sucesso!!!')
                
        if not GrauEscolar.objects.exists():
            graus = ['Etapa Creche', 'Ensino Fundamental I (Séries Iniciais)', 'Ensino Fundamental II (Séries Finais)' ]
            for g in graus:
                GrauEscolar.objects.create(
                    nome = g
                )
            print('GrauEscolar criado com sucesso!!!')

        if not Compatibilidade_EducaCenso.objects.exists():
            nivel = [
                'Berçário I (0 a 1 ano)',
                'Berçário II (1 a 2 anos)',
                'Maternal I (2 a 3 anos)',
                'Maternal II (3 a 4 anos)',
                'Pré I (ou Jardim I, 4 a 5 anos)',
                'Pré II (ou Jardim II, 5 a 6 anos)',
                '1º ano (6 a 7 anos)',
                '2º ano (7 a 8 anos)',
                '3º ano (8 a 9 anos)',
                '4º ano (9 a 10 anos)',
                '5º ano (10 a 11 anos)',
                '6º ano (11 a 12 anos)',
                '7º ano (12 a 13 anos)',
                '8º ano (13 a 14 anos)',
                '9º ano (14 a 15 anos)',
                'Ciclo I (inicial, para jovens e adultos que ainda não completaram o Ensino Fundamental)',
                'Ciclo II (avançado, para conclusão do Ensino Fundamental)'
            ]
            for nome in nivel:
                Compatibilidade_EducaCenso.objects.create(nome=nome)
            print('Compatibilidade criado com sucesso!!!')


        if not TiposRemanejamentos.objects.exists():
            tipos = [  
                ['Desistente/Evasão Escolar', 'Constatado que o aluno não frequenta mais as aulas há bastante tempo'],
                ['Transferido', 'O aluno foi transferido para outra escola'],
                ['Mudança de Turma', 'O aluno mudou para outra turma da mesma escola']
            ]
            for n, m in tipos:
                TiposRemanejamentos.objects.create(
                    nome = n,
                    description = m
                )
            print('Tipos Remanejamento criado com sucesso!!!')

        # Cria os registros Deficiencia_aluno se não existirem
        if not Deficiencia_aluno.objects.exists():
            deficiencias = ['Física', 'Mental', 'Auditiva', 'Visual', 'Nenhuma']
            Deficiencia_aluno.objects.bulk_create([Deficiencia_aluno(nome=deficiencia) for deficiencia in deficiencias])
            print('Deficiencia aluno criado com sucesso!!!')

        # Cria os registros Disciplina se não existirem
        if not Disciplina.objects.exists():
            disciplinas = [
                ('Língua Portuguesa', 1), ('Língua Inglesa', 2), ('Matemática', 3), ('Ciências', 4),
                ('Geografia', 5), ('História', 6), ('Educação Ambiental', 7), ('Educação Artística', 8),
                ('Educação Física', 9)
            ]
            Disciplina.objects.bulk_create([Disciplina(nome=nome, ordem_historico=ordem) for nome, ordem in disciplinas])
            print('Disciplina criado com sucesso!!!')
        

        # Cria os registros GrauEscolar se não existirem
        if not Serie_Escolar.objects.exists():        
            try:
                et = GrauEscolar.objects.get(nome='Etapa Creche')
                f1 = GrauEscolar.objects.get(nome='Ensino Fundamental I (Séries Iniciais)')
                f2 = GrauEscolar.objects.get(nome='Ensino Fundamental II (Séries Finais)')                    
                compatibilidades = list(Compatibilidade_EducaCenso.objects.all())

                if len(compatibilidades) < 17:
                    print("Não há compatibilidade suficiente registrada em Compatibilidade_EducaCenso.")
                    return

                series = [
                    ('G1', et, compatibilidades[0]),
                    ('G2', et, compatibilidades[1]),
                    ('G3', et, compatibilidades[2]),
                    ('G4', et, compatibilidades[3]),
                    ('G5', et, compatibilidades[4]),
                    ('G6', et, compatibilidades[5]),
                    ('1 ano', f1, compatibilidades[6]),
                    ('2 ano', f1, compatibilidades[7]),
                    ('3 ano', f1, compatibilidades[8]),
                    ('4 ano', f1, compatibilidades[9]),
                    ('5 ano', f1, compatibilidades[10]),
                    ('6 ano', f2, compatibilidades[11]),
                    ('7 ano', f2, compatibilidades[12]),
                    ('8 ano', f2, compatibilidades[13]),
                    ('9 ano', f2, compatibilidades[14]),
                    ('Ciclo I', f1, compatibilidades[15]),
                    ('Ciclo II', f2, compatibilidades[16])
                ]

                for nome, nivel, compatibilidade in series:
                    Serie_Escolar.objects.create(
                        nome=nome,
                        nivel_escolar=nivel,
                        compatibilidade_EducaCenso=compatibilidade
                    )
                print('Serie Escolar criado com sucesso!!!')

            except GrauEscolar.DoesNotExist:
                # Handle the case where GrauEscolar entries are not found
                print("Alguns dos registros de GrauEscolar não foram encontrados.")
            


        # Cria os registros TamanhoRoupa se não existirem
        if not TamanhoRoupa.objects.exists():
            tamanhos = [
                {'nome': 'PP', 'descricao': 'Tamanho extra pequeno', 'largura': 40, 'altura': 60, 'comprimento': 30, 'peso': 0.2},
                {'nome': 'P', 'descricao': 'Tamanho pequeno', 'largura': 45, 'altura': 65, 'comprimento': 35, 'peso': 0.3},
                {'nome': 'M', 'descricao': 'Tamanho médio', 'largura': 50, 'altura': 70, 'comprimento': 40, 'peso': 0.4},
                {'nome': 'G', 'descricao': 'Tamanho grande', 'largura': 55, 'altura': 75, 'comprimento': 45, 'peso': 0.5},
                {'nome': 'GG', 'descricao': 'Tamanho extra grande', 'largura': 60, 'altura': 80, 'comprimento': 50, 'peso': 0.6}
            ]
            TamanhoRoupa.objects.bulk_create([TamanhoRoupa(**tamanho) for tamanho in tamanhos])
            print('Tamanho Roupa com sucesso!!!')

        # Cria o registro Cursos se não existir
        if not Cursos.objects.exists():
            Cursos.objects.create(nome="Licenciatura em Pedagogia", nivel=2)
            print('Cursos criado com sucesso!!!')

        # Cria o registro Faculdades_ou_Escolas se não existir
        if not Faculdades_ou_Escolas.objects.exists():
            Faculdades_ou_Escolas.objects.create(nome="UNEB - Universidade Estadual da Bahia")
            print('Faculdes ou Escola criado com sucesso!!!')

        # Cria os registros Trimestre se não existirem
        if not Trimestre.objects.exists():
            ano_letivo = AnoLetivo.objects.get(id=1)
            trimestres = [
                ('I Trimestre', ano_letivo, False),
                ('II Trimestre', ano_letivo, False),
                ('III Trimestre', ano_letivo, False),
                ('Final', ano_letivo, True)
            ]
            Trimestre.objects.bulk_create([Trimestre(numero_nome=num, ano_letivo=ano, final=final) for num, ano, final in trimestres])
            print('Trimestre criado com sucesso!!!')

        # Cria os registros DiaSemana se não existirem
        if not DiaSemana.objects.exists():
            dias_da_semana = [
                (1, 'Segunda-feira'), (2, 'Terça-feira'), (3, 'Quarta-feira'), (4, 'Quinta-feira'),
                (5, 'Sexta-feira'), (6, 'Sábado'), (7, 'Domingo')
            ]
            DiaSemana.objects.bulk_create([DiaSemana(numero_dia=num, nome_dia=nome) for num, nome in dias_da_semana])   
            print('Dia da Semana criado com sucesso!!!')  
        print(f"Todos registros criados com sucesso")













    except Exception as e:
        print(f"Erro ao adicionar registros: {e}")

if __name__ == '__main__':
    iniciar_registros()
