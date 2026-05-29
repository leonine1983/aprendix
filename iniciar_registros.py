# iniciar_registros.py

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sme.settings")
django.setup()

from admin_acessos.models import MessageUser, NomeclaturaJanelas
from rh.models import *
from gestao_escolar.models import *
from django.contrib.auth.models import User, Group
from datetime import datetime


# ══════════════════════════════════════════════════════════════════
# 🔐 GERAÇÃO DAS CHAVES VAPID
# ══════════════════════════════════════════════════════════════════

def gerar_chaves_vapid():
    """
    Gera as chaves VAPID necessárias para Web Push Notifications.

    - Salva a chave privada em vapid_private.pem (nunca versionar este arquivo).
    - Salva a chave pública em base64url em vapid_public.txt.
    - Injeta VAPID_PUBLIC_KEY e VAPID_PRIVATE_KEY no settings em tempo de execução.
    - Exibe instruções para colar as variáveis no settings.py / .env.
    """

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PRIVATE_PEM = os.path.join(BASE_DIR, "vapid_private.pem")
    PUBLIC_TXT  = os.path.join(BASE_DIR, "vapid_public.txt")

    print("\n──── 🔐 VAPID ────")

    # ── já existem? ──────────────────────────────────────────────
    if os.path.exists(PRIVATE_PEM) and os.path.exists(PUBLIC_TXT):
        print("Chaves VAPID já existem — pulando geração.")

        with open(PUBLIC_TXT) as f:
            pub_key = f.read().strip()

        _aplicar_vapid_no_settings(PRIVATE_PEM, pub_key)
        return

    # ── gera novas chaves ─────────────────────────────────────────
    try:
        from py_vapid import Vapid
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
        import base64
    except ImportError:
        print(
            "⚠️  pywebpush / py_vapid não instalado.\n"
            "   Execute:  pip install pywebpush\n"
            "   e rode este script novamente."
        )
        return

    vapid = Vapid()
    vapid.generate_keys()
    vapid.save_key(PRIVATE_PEM)

    # Chave pública em base64url sem padding (formato exigido pelo navegador)
    pub_bytes = vapid.public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
    pub_key   = base64.urlsafe_b64encode(pub_bytes).decode().rstrip("=")

    with open(PUBLIC_TXT, "w") as f:
        f.write(pub_key)

    print(f"✅ Chave privada salva em : {PRIVATE_PEM}")
    print(f"✅ Chave pública salva em : {PUBLIC_TXT}")
    print(f"\n   VAPID_PUBLIC_KEY  = \"{pub_key}\"")
    print(f"   VAPID_PRIVATE_KEY = \"{PRIVATE_PEM}\"  (caminho do .pem)")
    print(
        "\n   ⚠️  Adicione as linhas acima ao seu settings.py (ou .env).\n"
        "   ⚠️  NUNCA versione vapid_private.pem — adicione-o ao .gitignore.\n"
    )

    _aplicar_vapid_no_settings(PRIVATE_PEM, pub_key)


def _aplicar_vapid_no_settings(private_pem_path: str, public_key: str):
    """Injeta as variáveis VAPID no settings em tempo de execução (sem reiniciar)."""
    from django.conf import settings

    if not getattr(settings, "VAPID_PUBLIC_KEY", ""):
        settings.VAPID_PUBLIC_KEY = public_key

    if not getattr(settings, "VAPID_PRIVATE_KEY", ""):
        settings.VAPID_PRIVATE_KEY = private_pem_path

    if not getattr(settings, "VAPID_CLAIMS", None):
        settings.VAPID_CLAIMS = {"sub": "mailto:admin@prefeitura.gov.br"}

    print("VAPID carregado no settings com sucesso.")


# ══════════════════════════════════════════════════════════════════
# 📦 REGISTROS PADRÃO
# ══════════════════════════════════════════════════════════════════

def iniciar_registros():
    try:
        # ── VAPID (deve ser o primeiro passo) ─────────────────────
        gerar_chaves_vapid()

        # ── ADMIN ACESSOS ─────────────────────────────────────────
        print("\n──── Inicializando Admin Acessos ────")

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

        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from django.db import transaction
        from django.apps import apps

        @transaction.atomic
        def configurar_grupos_institucionais():
            group_names = [
                "Nutricionista", "Merendeira", "Admin", "Professor",
                "Diretor", "Secretario", "Coordenador", "Aluno",
            ]

            grupos = {}
            for group_name in group_names:
                grupo, created = Group.objects.get_or_create(name=group_name)
                grupos[group_name] = grupo
                status = "criado" if created else "já existente"
                print(f"Grupo {status}: {group_name}")

            permissoes_merenda = Permission.objects.filter(content_type__app_label="merendaEscolar")
            grupos["Admin"].permissions.add(*permissoes_merenda)
            grupos["Nutricionista"].permissions.add(*permissoes_merenda)
            print(f"Permissões merendaEscolar → Admin e Nutricionista: {permissoes_merenda.count()}")

            app_config = apps.get_app_config("modulo_Merendeiras")
            permissoes_merendeira = []
            for model in app_config.get_models():
                ct = ContentType.objects.get_for_model(model)
                permissoes_merendeira.extend(Permission.objects.filter(content_type=ct))
            grupos["Merendeira"].permissions.add(*permissoes_merendeira)
            print(f"Permissões modulo_Merendeiras → Merendeira: {len(permissoes_merendeira)}")

            for app_label, grupo_nome in [
                ("modulo_professor",    "Professor"),
                ("modulo_aluno",        "Aluno"),
                ("gestao_escolar",      "Diretor"),
                ("gestao_escolar",      "Secretario"),
                ("modulo_coordenacao",  "Coordenador"),
            ]:
                perms = Permission.objects.filter(content_type__app_label=app_label)
                grupos[grupo_nome].permissions.add(*perms)
                print(f"Permissões {app_label} → {grupo_nome}: {perms.count()}")

            print("Grupos configurados com sucesso.")

        configurar_grupos_institucionais()

        # ── RH ────────────────────────────────────────────────────
        print("\n──── Inicializando RH ────")

        if not Config_plataforma.objects.exists():
            Config_plataforma.objects.create(nome_sistema='Meu Sistema', versao='1.0.0')
            print("Config plataforma criada.")

        if not Uf_Unidade_Federativa.objects.exists():
            uf_estados = [
                ('AC','Acre'),('AL','Alagoas'),('AM','Amazonas'),('AP','Amapá'),
                ('BA','Bahia'),('CE','Ceará'),('DF','Distrito Federal'),('ES','Espírito Santo'),
                ('GO','Goiás'),('MA','Maranhão'),('MG','Minas Gerais'),('MS','Mato Grosso do Sul'),
                ('MT','Mato Grosso'),('PA','Pará'),('PB','Paraíba'),('PE','Pernambuco'),
                ('PI','Piauí'),('PR','Paraná'),('RJ','Rio de Janeiro'),('RN','Rio Grande do Norte'),
                ('RO','Roraima'),('RR','Rondônia'),('RS','Rio Grande do Sul'),('SC','Santa Catarina'),
                ('SE','Sergipe'),('SP','São Paulo'),('TO','Tocantins'),
            ]
            Uf_Unidade_Federativa.objects.bulk_create(
                [Uf_Unidade_Federativa(sigla=s, estado=e) for s, e in uf_estados]
            )
            print("Estados criados.")

        if not Cidade.objects.exists():
            try:
                uf = Uf_Unidade_Federativa.objects.get(sigla='BA')
                Cidade.objects.create(nome_estado=uf, nome_cidade='Vera Cruz')
                print("Cidade criada.")
            except Uf_Unidade_Federativa.DoesNotExist:
                print("UF BA não encontrada.")

        if not Bairro.objects.exists():
            try:
                cidade = Cidade.objects.get(nome_cidade='Vera Cruz')
                bairros = sorted([
                    "Aratuba","Baiacu","Barra do Gil","Barra do Pote","Berlinque",
                    "Cacha Pregos","Campinas","Cine","Conceição","Coroa",
                    "Gamboa","Ilhota","Juerana","Mar Grande","Matarandiba",
                    "Ponta Grossa","Porrãozinho",
                ])
                Bairro.objects.bulk_create(
                    [Bairro(nome_cidade=cidade, nome_bairro=b) for b in bairros]
                )
                print("Bairros criados.")
            except Cidade.DoesNotExist:
                print("Cidade Vera Cruz não encontrada.")

        if not Prefeitura.objects.exists():
            try:
                cidade = Cidade.objects.get(nome_cidade='Vera Cruz')
                estado = Uf_Unidade_Federativa.objects.get(sigla='BA')
                Prefeitura.objects.create(
                    nome='Prefeitura Municipal de Vera Cruz',
                    instituto='Secretaria Municipal da Educação',
                    cidade=cidade, estado=estado,
                    endereco='Av. Te encontro lá',
                    pessoa_publica='Igor Pinho', brasao='',
                )
                print("Prefeitura criada.")
            except (Cidade.DoesNotExist, Uf_Unidade_Federativa.DoesNotExist):
                print("Cidade ou UF não encontrada para criar Prefeitura.")

        if not Ano.objects.exists():
            try:
                prefeitura = Prefeitura.objects.get(nome='Prefeitura Municipal de Vera Cruz')
                Ano.objects.create(
                    prefeitura=prefeitura, ano='2025',
                    data_inicio=datetime.strptime('12/03/2025', '%d/%m/%Y').date(),
                    data_fim=datetime.strptime('19/12/2025', '%d/%m/%Y').date(),
                )
                print('Ano Letivo criado.')
            except Prefeitura.DoesNotExist:
                print("Prefeitura não encontrada.")

        if not Profissao.objects.exists():
            nome_descreve = [
                ('Diretor Escolar', 'Profissional encarregado da administração e gestão de uma escola.'),
                ('Vice-Diretor Escolar', 'Profissional que auxilia o diretor escolar.'),
                ('Coordenador Escolar', 'Profissional que supervisiona as operações educacionais.'),
                ('Secretária escolar', 'Profissional responsável por tarefas administrativas.'),
                ('Professor', 'Profissional dedicado à educação e ao ensino.'),
                ('Reserva Técnica', 'Profissional responsável por apoiar a infraestrutura.'),
                ('Auxiliar de Classe', 'Colaborador que assiste o professor no dia a dia.'),
                ('Merendeira', 'Funcionária responsável pela preparação e distribuição das refeições.'),
                ('Técnica em alimentação escolar', 'Profissional especializada em planejar refeições nutritivas.'),
                ('Porteiro escolar', 'Profissional encarregado de monitorar o acesso à escola.'),
                ('Auxiliar Administrativo Escolar', 'Profissional de suporte administrativo.'),
            ]
            Profissao.objects.bulk_create(
                [Profissao(nome_profissao=n, descricao=d) for n, d in nome_descreve]
            )
            print('Profissões criadas.')

        if not Sexo.objects.exists():
            Sexo.objects.bulk_create([Sexo(nome=s) for s in [
                'Masculino (cisgênero)','Feminino (cisgênero)','Homem trans','Mulher trans',
                'Travesti','Não-binário','Agênero','Gênero-fluido','Bigênero',
                'Demiboy','Demigirl','Intersexo','Outro','Prefere não informar',
            ]])
            print('Gêneros criados.')

        if not Escola.objects.exists():
            prefeitura = Prefeitura.objects.first()
            if prefeitura:
                escolas_data = [
                    ("Escola Municipal Geralda Maria", True),
                    ("Colégio Municipal de Vera Cruz", True),
                    ("Centro de Atendimento Educacional Especializado Dr Nicandro Moreira de Macedo", False),
                    ("Centro Municipal de Educação Infantil de Cacha Pregos", False),
                    ("Colégio Municipal Telma Régis de Andrade", True),
                    ("Colégio Municipal Geralda Maria da Conceição", True),
                    ("Colégio Municipal Jarbas Passarinho", False),
                    ("Colégio Municipal Luiz Eduardo Magalhães", True),
                    ("Colégio Municipal Professora Daulia Angélica de Souza Santos", True),
                    ("Creche de Jiribatuba", False),
                    ("Creche Escola Municipal Educandário Tio Aurélio", False),
                    ("Creche Escola Municipal Elza Galvão", False),
                    ("Creche Escola Municipal Professora Nice Maria Vinagre de Oliveira", False),
                    ("Creche Escola Municipal Simone Trigano", False),
                    ("Creche Escola Municipal Vovó Nida", False),
                    ("Creche Escola Municipal Vovô Nizio", False),
                    ("Escola Clementino Lima", False),
                    ("Escola Comunitária Aquilino dos Santos", False),
                    ("Escola Dr José Eugênio Mendes Figueiredo", False),
                    ("Escola Ivandite Pires Miranda Costa", False),
                    ("Escola Major Everaldo Calazans de Almeida", False),
                    ("Escola Manoel Januário de Lima", False),
                    ("Escola Municipal Presidente Emílio Garrastazu Médici", False),
                    ("Escola Municipal Almiro Antunes de Brito", False),
                    ("Escola Municipal Antônio Hermenegildo de Sena Pereira", False),
                    ("Escola Municipal Argérico Rocha Borges", False),
                    ("Escola Municipal Aureliano de Azevedo Monteiro", False),
                    ("Escola Municipal Braz Felisberto de Santana", False),
                    ("Escola Municipal de Ponta Grossa", False),
                    ("Escola Municipal Gaudêncio Acelino Marques", False),
                    ("Escola Municipal Gezilda Alves de Souza", False),
                    ("Escola Municipal Guilherme Franco Guimarães", False),
                    ("Escola Municipal Hilton Rodrigues", False),
                    ("Escola Municipal João José de Macedo", True),
                    ("Escola Municipal Joaquim Barreto de Araújo", False),
                    ("Escola Municipal Juvenal Galvão", False),
                    ("Escola Municipal Margarida Moreira", False),
                    ("Escola Municipal Nova Divineia", False),
                    ("Escola Municipal Olga Seabra", False),
                    ("Escola Municipal Padre Ignácio Alves Pereira", False),
                    ("Escola Municipal Professor Jorge Calmon", False),
                    ("Escola Municipal Raimundo Afonso Borges", False),
                    ("Escola Municipal Turma da Mônica", False),
                    ("Escola Narciso Francisco de Pinho", False),
                    ("Escola Sede Social do Riachinho", False),
                    ("Escola Voluntárias Sociais da Bahia", False),
                    ("Ginásio Municipal Estelita Eusébia Santiago dos Santos", True),
                ]
                escolas_criadas = Escola.objects.bulk_create(
                    [Escola(prefeitura=prefeitura, nome_escola=n, fund2=t) for n, t in escolas_data]
                )
                for escola in escolas_criadas:
                    Escola_admin.objects.get_or_create(nome=escola)
                print(f"{len(escolas_criadas)} escolas criadas.")

        # ── GESTÃO ESCOLAR ────────────────────────────────────────
        print("\n──── Inicializando Gestão Escolar ────")

        if not Cargo.objects.exists():
            cargos = [
                'Diretor','Vice-Diretor','Coordenador','Professor',
                'Auxiliar-Administrativo-I','Auxiliar-Administrativo-II',
                'Tecnico-em-Multimeitos-Didáticos','Tecnico-em-Merenda-Escolar',
                'Auxiliar-de-Classe','Servente-de-limpeza','Monitor-de-Informática',
                'Merendeira','Porteiro','Estagiário',
            ]
            Cargo.objects.bulk_create([Cargo(nome=n) for n in cargos])
            print('Cargos criados.')

        if not Etnia.objects.exists():
            Etnia.objects.bulk_create(
                [Etnia(nome=e) for e in ['Branca','Negra','Parda','Amarela','Indigena','Não declarado']]
            )
            print('Etnias criadas.')

        if not Nacionalidade.objects.exists():
            Nacionalidade.objects.bulk_create(
                [Nacionalidade(nome=n) for n in ['Brasileira','Brasileiro nascido no exterior','Mexicano']]
            )
            print('Nacionalidades criadas.')

        if not Pais_origem.objects.exists():
            Pais_origem.objects.bulk_create(
                [Pais_origem(nome=p) for p in ['Brasil','Japão','México']]
            )
            print('Países de origem criados.')

        if not GrauEscolar.objects.exists():
            for g in ['Etapa Creche','Ensino Fundamental I (Séries Iniciais)','Ensino Fundamental II (Séries Finais)']:
                GrauEscolar.objects.get_or_create(nome=g)
            print('GrauEscolar criado.')

        if not Compatibilidade_EducaCenso.objects.exists():
            niveis = [
                'Berçário I (0 a 1 ano)','Berçário II (1 a 2 anos)',
                'Maternal I (2 a 3 anos)','Maternal II (3 a 4 anos)',
                'Pré I (ou Jardim I, 4 a 5 anos)','Pré II (ou Jardim II, 5 a 6 anos)',
                '1º ano (6 a 7 anos)','2º ano (7 a 8 anos)','3º ano (8 a 9 anos)',
                '4º ano (9 a 10 anos)','5º ano (10 a 11 anos)','6º ano (11 a 12 anos)',
                '7º ano (12 a 13 anos)','8º ano (13 a 14 anos)','9º ano (14 a 15 anos)',
                'Ciclo I (inicial, para jovens e adultos que ainda não completaram o Ensino Fundamental)',
                'Ciclo II (avançado, para conclusão do Ensino Fundamental)',
            ]
            for nome in niveis:
                Compatibilidade_EducaCenso.objects.create(nome=nome)
            print('Compatibilidade_EducaCenso criada.')

        if not TiposRemanejamentos.objects.exists():
            for n, m in [
                ('Desistente/Evasão Escolar', 'Constatado que o aluno não frequenta mais as aulas'),
                ('Transferido', 'O aluno foi transferido para outra escola'),
                ('Mudança de Turma', 'O aluno mudou para outra turma da mesma escola'),
            ]:
                TiposRemanejamentos.objects.create(nome=n, description=m)
            print('TiposRemanejamentos criados.')

        if not Deficiencia_aluno.objects.exists():
            Deficiencia_aluno.objects.bulk_create(
                [Deficiencia_aluno(nome=d) for d in ['Física','Mental','Auditiva','Visual','Nenhuma']]
            )
            print('Deficiencias criadas.')

        if not Disciplina.objects.exists():
            disciplinas = [
                ('Língua Portuguesa',1),('Língua Inglesa',2),('Matemática',3),
                ('Ciências',4),('Geografia',5),('História',6),
                ('Educação Ambiental',7),('Educação Artística',8),('Educação Física',9),
            ]
            Disciplina.objects.bulk_create(
                [Disciplina(nome=n, ordem_historico=o) for n, o in disciplinas]
            )
            print('Disciplinas criadas.')

        if not Serie_Escolar.objects.exists():
            try:
                et = GrauEscolar.objects.get(nome='Etapa Creche')
                f1 = GrauEscolar.objects.get(nome='Ensino Fundamental I (Séries Iniciais)')
                f2 = GrauEscolar.objects.get(nome='Ensino Fundamental II (Séries Finais)')
                compat = list(Compatibilidade_EducaCenso.objects.all())
                if len(compat) >= 17:
                    series = [
                        ('G1',et,compat[0]),('G2',et,compat[1]),('G3',et,compat[2]),
                        ('G4',et,compat[3]),('G5',et,compat[4]),('G6',et,compat[5]),
                        ('1 ano',f1,compat[6]),('2 ano',f1,compat[7]),('3 ano',f1,compat[8]),
                        ('4 ano',f1,compat[9]),('5 ano',f1,compat[10]),('6 ano',f2,compat[11]),
                        ('7 ano',f2,compat[12]),('8 ano',f2,compat[13]),('9 ano',f2,compat[14]),
                        ('Ciclo I',f1,compat[15]),('Ciclo II',f2,compat[16]),
                    ]
                    for nome, nivel, compatibilidade in series:
                        Serie_Escolar.objects.create(
                            nome=nome,
                            nivel_escolar=nivel,
                            compatibilidade_EducaCenso=compatibilidade,
                        )
                    print('Serie Escolar criada.')
            except GrauEscolar.DoesNotExist:
                print("GrauEscolar não encontrado.")

        if not TamanhoRoupa.objects.exists():
            tamanhos = [
                {'nome':'PP','descricao':'Extra pequeno','largura':40,'altura':60,'comprimento':30,'peso':0.2},
                {'nome':'P', 'descricao':'Pequeno',      'largura':45,'altura':65,'comprimento':35,'peso':0.3},
                {'nome':'M', 'descricao':'Médio',        'largura':50,'altura':70,'comprimento':40,'peso':0.4},
                {'nome':'G', 'descricao':'Grande',       'largura':55,'altura':75,'comprimento':45,'peso':0.5},
                {'nome':'GG','descricao':'Extra grande', 'largura':60,'altura':80,'comprimento':50,'peso':0.6},
            ]
            TamanhoRoupa.objects.bulk_create([TamanhoRoupa(**t) for t in tamanhos])
            print('TamanhoRoupa criado.')

        if not Cursos.objects.exists():
            Cursos.objects.create(nome="Licenciatura em Pedagogia", nivel=2)
            print('Curso criado.')

        if not Faculdades_ou_Escolas.objects.exists():
            Faculdades_ou_Escolas.objects.create(nome="UNEB - Universidade Estadual da Bahia")
            print('Faculdade criada.')

        if not Trimestre.objects.exists():
            try:
                ano_letivo = AnoLetivo.objects.get(id=1)
                Trimestre.objects.bulk_create([
                    Trimestre(numero_nome=n, ano_letivo=ano_letivo, final=f)
                    for n, f in [
                        ('I Trimestre',False),('II Trimestre',False),
                        ('III Trimestre',False),('Final',True),
                    ]
                ])
                print('Trimestres criados.')
            except AnoLetivo.DoesNotExist:
                print("AnoLetivo id=1 não encontrado.")

        if not DiaSemana.objects.exists():
            DiaSemana.objects.bulk_create([
                DiaSemana(numero_dia=n, nome_dia=d)
                for n, d in [
                    (1,'Segunda-feira'),(2,'Terça-feira'),(3,'Quarta-feira'),
                    (4,'Quinta-feira'),(5,'Sexta-feira'),(6,'Sábado'),(7,'Domingo'),
                ]
            ])
            print('Dias da semana criados.')

        print("\n✅ Todos os registros criados com sucesso.")

    except Exception as e:
        print(f"\n❌ Erro ao adicionar registros: {e}")
        raise


if __name__ == '__main__':
    iniciar_registros()