from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from rh.models import Ano as AnoLetivo, Uf_Unidade_Federativa, Sexo, Bairro, Cidade, Encaminhamentos
from ckeditor_uploader.fields import RichTextUploadingField


class Cargo(models.Model):
    nome = models.CharField(max_length=30)
    def __str__(self):
        return self.nome
    
    
class Etnia(models.Model):
    nome = models.CharField(max_length=30)   
    def __str__(self):
        return self.nome
    

class Nacionalidade(models.Model):
    nome = models.CharField(max_length=30)   
    def __str__(self):
        return self.nome
    

class Pais_origem(models.Model):
    nome = models.CharField(max_length=30)  
    def __str__(self):
        return self.nome
    

class Deficiencia_aluno(models.Model):
    nome = models.CharField(max_length=30)  
    def __str__(self):
        return self.nome
    
choices = {
    
    ('1','A+'),
    ('2','A-'),
    ('3','B+'),
    ('4','B-'),
    ('5','AB+'),
    ('6','AB-'),
    ('7','O+'),
    ('8','O-'),
    ('0','Não informado')
}

choice_uf = {
    (1, 'AC'),
    (2, 'AL'),
    (3, 'AM'),
    (4, 'AP'),
    (5, 'BA'),
    (6, 'CE'),
    (7, 'DF'),
    (8, 'ES'),
    (9, 'GO'),
    (10, 'MA'),
    (11, 'MG'),
    (12, 'MS'),
    (13, 'MT'),
    (14, 'PA'),
    (15, 'PB'),
    (16, 'PE'),
    (17, 'PI'),
    (18, 'PR'),
    (19, 'RJ'),
    (20, 'RN'),
    (21, 'RO'),
    (22, 'RR'),
    (23, 'RS'),
    (24, 'SC'),
    (25, 'SE'),
    (26, 'SP'),
    (27, 'TO'),
}

choice_estado_civil = {
    ('1', 'Solteiro'),
    ('2', 'Casado'),
    ('3', 'Separado'),
    ('4', 'Divorciado'),
    ('5', 'Viúvo'),
    ('6', 'União Estável'),
}

choice_certidao = {
    ('1', 'Nascimento'),
    ('2', 'Casamento'),
    ('3', 'Outras')
}

choice_modelo_certidao = {
    ('1', 'Antigo'),
    ('2', 'Novo'),
    ('3', 'Nenhuma')
}

choice_justifica_falta_document= {
    ('1', 'o(a) aluno(a) não possui os documentos pessoais solicitados'),
    ('2', 'A escola não dispõe ou não recebeu os docum. pessoais do(a) aluno(a)')    
}

choice_local_diferenciado= {
    ('1', 'Não está em área de localização diferenciada'),
    ('2', 'Área de assentamento'),
    ('3', 'Terra indígena'),
    ('4', 'Área remanescente de quilombos'),    
    ('5', 'Área de povos e comunidades tradicionais'),  
}

class Alunos(models.Model):
    nome_completo = models.CharField(max_length=120, null=False, default='Nome completo do aluno', verbose_name='Nome completo do aluno*')    
    nome_social = models.CharField(max_length=30, null=True, blank=True, default='')
    sexo = models.ForeignKey(Sexo, on_delete= models.CASCADE, verbose_name='Gênero sexual do aluno*', null=True)
    data_nascimento = models.DateField(verbose_name='Data de Nascimento*', null=True)    
    idade = models.IntegerField(null=True, blank=True)
    etnia = models.ForeignKey(Etnia, null=True, on_delete=models.CASCADE, verbose_name='Etnia do aluno*:')
    #aluno_inativo = models.BooleanField(default=False, null=True)
    tel_celular_aluno = models.CharField(max_length=30, null=False,  verbose_name='Nº de telefone do aluno*')    
    email = models.EmailField(max_length=200, null=False, verbose_name='Email*')
    rua = models.CharField(max_length=30, null=False, default='Av., Rua, Travessa')
    bairro = models.ForeignKey(Bairro, null=True, on_delete=models.CASCADE)
    cidade = models.ForeignKey(Cidade, null=True, on_delete=models.CASCADE)    
    cidade_nascimento = models.ForeignKey(Cidade, related_name="cidade_nascimento",verbose_name='Cidade onde nasceu', null=True, on_delete=models.CASCADE)
    estado = models.ForeignKey(Uf_Unidade_Federativa, related_name="estado_nascimento",verbose_name='Estado onde nasceu', null=True, on_delete=models.CASCADE)
    nome_mae = models.CharField(max_length=120, null=False, default='Nome completo da Mãe', verbose_name='Nome da Mãe*')
    tel_celular_mae = models.CharField(max_length=30, null=True, verbose_name='Nº do celular do mãe*')
    nome_pai = models.CharField(max_length=120, null=True, default='Nome completo da Pai')
    tel_celular_pai = models.CharField(max_length=30, null=True)    
    naturalidade = models.CharField(max_length=30, null=False, default='Cidade onde nasceu')
    nacionalidade = models.ForeignKey(Nacionalidade, on_delete=models.CASCADE, default=1, verbose_name='Nacionalidade*')
    aluno_exterior = models.BooleanField(default=False, verbose_name="Marque se o aluno veio do Exterior")
    pais_origem = models.ForeignKey(Pais_origem, blank=True, null=True, on_delete=models.CASCADE)
    data_entrada_no_pais= models.DateField(null=True, blank=True)  
    documento_estrangeiro = models.CharField(max_length=30, null=True, blank=True)
    deficiencia_aluno = models.ForeignKey(Deficiencia_aluno, on_delete=models.CASCADE, null=True, verbose_name='Informe se o aluno possui deficiência*')    
    tipo_sanguineo = models.CharField(max_length=3, choices=choices, null=True, )
    beneficiario_aux_Brasil = models.BooleanField(default=False,null=True, verbose_name='Selecione se o aluno é beneficiário do Bolsa Família/Aux. Brasil')
    necessita_edu_especial = models.BooleanField(default=False,null=True, verbose_name='Selecione se o aluno precisa de algum atendimento especial')
    sindrome_de_Down = models.BooleanField(default=False,null=True, verbose_name='Selecione se o aluno for portador de Síndrome de Down')
    quilombola = models.BooleanField(default=False,null=True, verbose_name='Selecione se o aluno possui deficiência')
    irmao_gemeo = models.BooleanField(default=False, null=True, verbose_name='Selecione se o aluno possui irmão(s) gêmeos')
    vacina_covid_19 = models.BooleanField(default=False, null=True,verbose_name='Selecione se o aluno tomou vacina contra a covid 19' )
    dose_vacina_covid_19 = models.IntegerField(null=True, blank=True, verbose_name='Preencha se o aluno tomou alguma dose da covid 19' )
    res_cadastro = models.CharField(max_length=120, null=True, default='Quem criou o cadastro')    
    res_atualiza_cadastro = models.CharField(max_length=120, null=True, default='Quem atualizou')    

    # Documentação
    RG = models.CharField(max_length=14, null=True, blank=True, default='000.000.00-00')    
    RG_emissao = models.DateField(null=True, blank=True, default=timezone.now)  
    RG_UF = models.ForeignKey(Uf_Unidade_Federativa, on_delete=models.CASCADE, null=True, blank=True)
    orgao_emissor = models.CharField(max_length=5, null=True, blank=True)

    renda_familiar = models.CharField(max_length=7, null=True, blank=True)
    #situacao_familiar = models.CharField(max_length=15, null=True, blank=True)
    CPF = models.CharField(max_length=14, null=True, blank=True, default='000.000.000-00')   

    login_aluno = models.CharField(max_length=10, null=True, blank=True)     
    senha = models.CharField(max_length=10, null=True, blank=True, default='12345678')
    
    cartao_nacional_saude_cns = models.CharField(max_length=20, null=True, blank=True)
    nis = models.CharField(max_length=20, null=True, blank=True)    
    inep = models.CharField(max_length=15, null=True, blank=True)
    estado_civil = models.CharField(max_length=13, null=True, blank=True, choices=choice_estado_civil) 
    tipo_certidao = models.CharField(max_length=13, null=True, blank=True, choices=choice_certidao) 
    numero_certidao = models.CharField(max_length=15, null=True, blank=True, verbose_name='Certidão de Nascimento (Matrícula Única)')
    livro = models.CharField(max_length=10, null=True, blank=True)
    folha = models.CharField(max_length=10, null=True, blank=True)
    termo = models.CharField(max_length=10, null=True, blank=True)
    emissao = models.DateField(null=True, blank=True)
    distrito_certidao= models.CharField(max_length=20, null=True, blank=True)
    cartorio = models.CharField(max_length=100, null=True, blank=True)
    comarca = models.CharField(max_length=100, null=True, blank=True)
    cartorio_uf = models.ForeignKey(Uf_Unidade_Federativa, related_name='relatio_cartorio_UF', null=True, on_delete=models.CASCADE)
    justificativa_falta_document = models.CharField(max_length=2, choices=choice_justifica_falta_document, null=True, blank=True, verbose_name='Justificativa da falta de documentação')
    local_diferenciado = models.CharField(max_length=2, choices=choice_justifica_falta_document, null=True, blank=True, verbose_name='Local Diferenciado')
    obito = models.BooleanField(null=True, blank=True,default=False)
    data_obito = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nome_completo 


class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    ordem_historico = models.FloatField(null=True)
    n_A = models.BooleanField(verbose_name="Destacar como N/S (Não avaliado) nos impressos", default=False, null=True)
    faltas = models.BooleanField(verbose_name="Não permitir lançamento de faltas", default=False, null=True)
    notas = models.BooleanField(verbose_name="Não permitir lançamento de notas", default=False, null=True)
    historico_escolar = models.BooleanField(verbose_name="Não mostrar no histórico escolar", default=False, null=True)
    papeletas = models.BooleanField(verbose_name="Não mostrar em papeletas", default=False, null=True)
    ata_final = models.BooleanField(verbose_name="Não mostrar em Atas Finais", default=False, null=True)   

    class Meta:
        ordering = ['ordem_historico']

    def __str__(self):
        return self.nome


class Compatibilidade_EducaCenso(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

    @receiver(post_migrate)
    def createCompatibilidadeEdu(sender, **kwargs):
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


class GrauEscolar(models.Model):
    nome = models.CharField(max_length=30, verbose_name="Grau/Nível Escolar")

    def __str__(self):
        return self.nome

    @receiver(post_migrate)
    def criar_registerGrau(sender, **kwargs):
        if not GrauEscolar.objects.exists():
            grau = [
                'Etapa Creche',
                'Ensino Fundamental I (Séries Iniciais)',
                'Ensino Fundamental II (Séries Finais)'
            ]
            for nome in grau:
                GrauEscolar.objects.create(nome=nome)


class Serie_Escolar(models.Model):
    nome = models.CharField(max_length=30)
    nivel_escolar = models.ForeignKey(GrauEscolar, null=False, on_delete=models.CASCADE)
    compatibilidade_EducaCenso = models.ForeignKey(Compatibilidade_EducaCenso, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome

    @receiver(post_migrate)
    def criar_registerSerie(sender, **kwargs):
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

            except GrauEscolar.DoesNotExist:
                # Handle the case where GrauEscolar entries are not found
                print("Alguns dos registros de GrauEscolar não foram encontrados.")


turno = {
    ('Matutino', 'Matutino'),
    ('Verspertino', 'Verspertino'),
    ('Noturno', 'Noturno')
}


class Turmas(models.Model):
    nome = models.CharField(max_length=10)
    descritivo_turma = models.CharField(max_length=10, default='única')
    escola = models.ForeignKey('rh.Escola', on_delete=models.CASCADE)
    ano_letivo = models.ForeignKey(AnoLetivo, on_delete=models.CASCADE)
    serie =  models.ForeignKey(Serie_Escolar, on_delete=models.CASCADE)
    turno = models.CharField(choices=turno, null=False, default=1, max_length=12)        
    turma_multiserie = models.BooleanField(null=True, default=False)
    turma_concluida = models.BooleanField(null=True, default=False)
    quantidade_vagas = models.IntegerField(default=36) 
    vagas_disponiveis = models.IntegerField(null=True)

  
    def __str__(self):
        return f'{self.nome.upper()} {self.descritivo_turma.upper()}'

    def __lt__(self, other):
        """
        Método especial que permite comparar instâncias de Turmas.
        
        Este método é usado para determinar a ordem entre duas instâncias de Turmas
        ao classificá-las. Neste exemplo, estamos comparando as instâncias com base
        no atributo 'nome'. 
        """
        return self.nome < other.nome


niveis = {
    ('1', "Médio"),
    ('2', "Superior")
}


class Profissionais(models.Model):
    nome = models.ForeignKey('rh.Encaminhamentos', on_delete=models.CASCADE, null=True)
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome.encaminhamento.contratado.nome


class Cursos(models.Model):
    nome = models.CharField(max_length=30)
    nivel = models.CharField(choices=niveis, max_length=1)
    

class Faculdades_ou_Escolas(models.Model):
    nome = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.nome
   

class TurmaDisciplina(models.Model):
    turma = models.ForeignKey(Turmas, related_name='gradeTurma_related', on_delete=models.CASCADE, null=True)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, null=True)
    quant_aulas_semana = models.IntegerField(default=5, null=True)
    quant_aulas_dia = models.IntegerField(default=3, null=True)
    professor = models.ForeignKey(Encaminhamentos, related_name='gradeProfessor1_related', on_delete=models.PROTECT, null=True)
    professo2 = models.ForeignKey(Encaminhamentos, related_name='gradeProfessor2_related', on_delete=models.PROTECT, null=True, blank=True)
    reserva_tecnica = models.ForeignKey(Encaminhamentos, related_name='reservaTecnica_related',on_delete=models.PROTECT,  null=True, blank=True)
    auxiliar_classe = models.ForeignKey(Encaminhamentos, related_name='auxiliarClasse_related',on_delete=models.PROTECT, null=True, blank=True)

    carga_horaria_anual = models.IntegerField(null=True)
    limite_faltas = models.IntegerField(null=True)

    def __str__(self):
        return f'{self.disciplina.nome} - {self.professor}'


escola_fora = {
    ('1', 'Não recebe'),
    ('2', 'Em hospital'),
    ('3', 'Em domicílio')
}


class TamanhoRoupa(models.Model):
    nome = models.CharField(max_length=2)
    descricao = models.TextField(blank=True, null=True)
    largura = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    altura = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    comprimento = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.nome
    

class Matriculas(models.Model):
    cod_matricula = models.TextField(max_length=200, null=True, default='2023-001')
    aluno = models.ForeignKey(Alunos, related_name='related_matricula_alunos', on_delete=models.CASCADE)
    turma = models.ForeignKey(Turmas, related_name='related_matricula_turma', on_delete=models.CASCADE)
    camisa_tamanho = models.ForeignKey(TamanhoRoupa, related_name='related_camisa', null=True, on_delete=models.CASCADE)
    data_matricula = models.DateField(auto_now=True)
    escolarizacao_fora = models.CharField(choices=escola_fora, default=1, max_length=1)
    serie_multiseriada = models.ForeignKey(Serie_Escolar, null=True, blank=True, on_delete=models.CASCADE)
    data_afastamento_inicio = models.DateField(null=True)
    data_afastamento_fim = models.DateField(null=True)
    motivo_afastamento = models.TextField(max_length=200, null=True)
    calcula_media = models.BooleanField(default=True, null=True, blank=True)
    profissional_matricula = models.ForeignKey(User, related_name='related_matricula_alunos', null=True, on_delete=models.CASCADE)
    obervacao = RichTextUploadingField(null=True, blank=True)    
    calcula_media = models.BooleanField(default=True, null=True, blank=True)
    # Are de aprovacao do aluno no ano letivo
    aprovado_recupera = models.BooleanField(default=False)

    @receiver(post_save)
    def verifica_vagas(sender, instance, **kwargs):
        # Ensure the instance is of type Matriculas
        if isinstance(instance, Matriculas):
            turma = instance.turma
            # Calculate the number of existing matriculas for the turma
            existing_matriculas_count = turma.related_matricula_turma.count()
            # Update vagas_disponiveis
            turma.vagas_disponiveis = turma.quantidade_vagas - existing_matriculas_count
            turma.save()

    class Meta:
        ordering = ['aluno']

    def __str__(self):
        return self.aluno.nome_completo
    
  
class TiposRemanejamentos(models.Model):
    nome = models.CharField(max_length=26, null=True, verbose_name="Tipo de remanejamento")
    description = models.TextField(max_length=500, verbose_name="Descreve o tipo de remanejamento")

    def __str__(self):
        return self.nome
    
    @receiver(post_migrate)
    def createRegisterTR(sender, **kwargs):
        if not TiposRemanejamentos.objects.exists():
            tipos = [  
                ['Desistente', 'Constatado que o aluno não frequenta mais as aulas há bastante tempo'],
                ['Transferido', 'O aluno foi transferido para outra escola'],
                ['Mudança de Turma', 'O aluno mudou para outra turma da mesma escola']
            ]
            for n, m in tipos:
                TiposRemanejamentos.objects.create(
                    nome = n,
                    description = m
                )


class Remanejamento(models.Model):    
    tipo = models.ForeignKey(TiposRemanejamentos, null=True, on_delete=models.CASCADE)    
    aluno = models.ForeignKey(Matriculas, null=True, blank=True, on_delete=models.CASCADE)    
    description = models.TextField(max_length=500, verbose_name="Descreva o motivo do Remanejamento. Ex.: Escola para onde o aluno será remanejado e o porquê.")    
    turmaAnterior = models.CharField(max_length=20, null=True, blank=True, verbose_name="Turma anterior")
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tipo.nome


class Trimestre(models.Model):
    numero_nome = models.CharField(null=True, max_length=14)
    ano_letivo = models.ForeignKey(AnoLetivo, null=True, on_delete=models.CASCADE)
    final = models.BooleanField(default=False)     
    def __str__(self):
        return self.numero_nome
    

class Periodo(models.Model):
    escola = models.ForeignKey('rh.Escola', on_delete=models.CASCADE, null=True)
    turma = models.ForeignKey(Turmas, on_delete=models.CASCADE, null=True)
    nome_periodo = models.CharField(max_length=30, null=True)
    hora_inicio = models.TimeField(null=True)
    hora_fim = models.TimeField(null=True)

    def __str__(self):
        return f'{self.hora_inicio} - {self.hora_fim}'
    
    def __lt__(self, other):
        """
        Método especial que permite comparar instâncias de Periodo.
        
        Este método é usado para determinar a ordem entre duas instâncias de Periodo
        ao classificá-las. Neste exemplo, estamos comparando as instâncias com base
        na hora de início. 
        """
        return self.hora_inicio < other.hora_inicio
    

class Validade_horario(models.Model):    
    escola = models.ForeignKey('rh.Escola', related_name='escola_validade_related', on_delete=models.CASCADE, null=True)
    turma = models.ForeignKey(Turmas,null=True, related_name='turma_Validade_related', on_delete=models.CASCADE)  
    nome_validade = models.CharField(max_length=30)
    data_inicio = models.DateField(null=True)
    data_fim = models.DateField(null=True)     
    horario_ativo = models.BooleanField(default=False)

    def __str__(self):
        return (f'{self.nome_validade}: {self.data_inicio} a {self.data_fim}')
    

class DiaSemana(models.Model):
    nome_dia = models.CharField(max_length=10)
    numero_dia = models.IntegerField()
    
    class Meta:
        ordering = ['numero_dia']

    def __str__(self):
        return self.nome_dia
    

class Horario(models.Model):
    validade = models.ForeignKey(Validade_horario,null=True, related_name='turma_Horario_related', on_delete=models.CASCADE)  
    turma = models.ForeignKey(Turmas,null=True, related_name='turma_Horario_related', on_delete=models.CASCADE)  
    periodo = models.ForeignKey(Periodo, null=True,related_name='periodo_Horario_related', on_delete=models.CASCADE)       
    segunda = models.ForeignKey(TurmaDisciplina, related_name='segunda_prof', null=True, blank=True, on_delete=models.SET_NULL)
    terca = models.ForeignKey(TurmaDisciplina, related_name='terca_prof', null=True, blank=True, on_delete=models.SET_NULL)
    quarta = models.ForeignKey(TurmaDisciplina, related_name='quarta_prof', null=True, blank=True, on_delete=models.SET_NULL)
    quinta = models.ForeignKey(TurmaDisciplina, related_name='quinta_prof', null=True, blank=True, on_delete=models.SET_NULL)
    sexta = models.ForeignKey(TurmaDisciplina, related_name='sexta_prof', null=True, blank=True, on_delete=models.SET_NULL)   
  

    def __str__(self):
        return f"Horario - {self.turma} - {self.periodo}"
    

class Presenca(models.Model):
    horario = models.ForeignKey(Horario, related_name='presencas', on_delete=models.CASCADE)
    matricula = models.ForeignKey(Matriculas, related_name='presencas', on_delete=models.CASCADE)
    presente = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.matricula.aluno.nome_completo} - {self.horario} - {"Presente" if self.presente else "Ausente"}'

class SequenciaDidatica(models.Model):
    horario = models.ForeignKey(Horario, related_name='sequencias_didaticas', on_delete=models.CASCADE)
    descricao = models.TextField()

    def __str__(self):
        return f'Sequência didática em {self.horario.data} - {self.horario.turma_disciplina.disciplina.nome}' 


class GestaoTurmas(models.Model):
    aluno = models.ForeignKey(Matriculas, related_name='gestao_turmas_related', null=True, on_delete=models.CASCADE)
    grade = models.ForeignKey(TurmaDisciplina, null=True, on_delete=models.CASCADE)
    trimestre = models.ForeignKey(Trimestre, related_name='trimestre_related_turma', null=True, on_delete=models.CASCADE)
    notas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    faltas = models.IntegerField(null=True, blank=True)
    profissional_resp = models.CharField(max_length=40, null=True)
    data_hora_mod = models.DateTimeField(null=True)

    faltas_total = models.IntegerField(null=True, blank=True)
    recuperacao_final = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    media_final = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)   

    media_anterior_conselho_classe = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    conselho_classe = models.BooleanField(default=False)

    aprovado = models.BooleanField(default=False)

    def __str__(self):
        return self.aluno.aluno.nome_completo
    

# Disponibilização do CAAE -------------------------------------------------------------------------------------------------------------------------
class AtendimentoEspecializado(models.Model):
    nome = models.CharField(max_length=30, null=False)
    descricao = models.TextField(max_length=500)

    def __str__(self):
        return self.nome


class ProfissionaisCaae(models.Model):
    nome = models.ForeignKey('rh.Pessoas', on_delete=models.PROTECT)
    especialidade = models.CharField(max_length=100)
    crm = models.CharField(max_length=20, unique=True, blank=True, null=True)  # Registro profissional

    def __str__(self):
        return self.nome


class MatriculaCaae(models.Model):
    aluno = models.ForeignKey('Matriculas', related_name="caae_related_aluno", on_delete=models.PROTECT)
    profissional = models.ForeignKey(ProfissionaisCaae, related_name="profissionais_caae_related", on_delete=models.PROTECT)
    atendimento_especializado = models.ForeignKey(AtendimentoEspecializado, related_name="atendimentos", on_delete=models.PROTECT)
    profissional_matricula = models.ForeignKey(User, related_name='related_matricula_alunosCAee', null=True, on_delete=models.CASCADE)   
    data_matricula = models.DateField(auto_now=True)    
    data_atendimento = models.DateField(default=timezone.now)  # Data do atendimento
    observacoes = models.TextField(max_length=500, blank=True, null=True)  # Observações sobre o atendimento

    def __str__(self):
        return f'Atendimento de {self.aluno} por {self.profissional} em {self.data_atendimento}'


class Agendamento(models.Model):
    aluno = models.ForeignKey(MatriculaCaae, related_name="agendamentos", on_delete=models.PROTECT)
    profissional = models.ForeignKey(ProfissionaisCaae, related_name="agendamentos_profissional", on_delete=models.PROTECT)
    atendimento_especializado = models.ForeignKey(AtendimentoEspecializado, related_name="agendamentos", on_delete=models.PROTECT)
    
    data_agendamento = models.DateTimeField()  # Data e hora do agendamento
    status = models.CharField(max_length=20, choices=[('agendado', 'Agendado'), ('realizado', 'Realizado'), ('cancelado', 'Cancelado')], default='agendado')

    def __str__(self):
        return f'Agendamento de {self.aluno} com {self.profissional} em {self.data_agendamento}'



# REGISTROS INICIAIS ---------------------

@receiver(post_migrate)
def post_migrate_setup(sender, **kwargs):
    if sender.name != 'gestao_escolar':  # Verifica se o app é 'gestao_escolar'
        return

    # Cria os registros Cargo se não existirem
    if not Cargo.objects.exists():
        cargos = [
            'Diretor', 'Vice-Diretor', 'Coordenador', 'Professor', 'Auxiliar-Administrativo-I',
            'Auxiliar-Administrativo-II', 'Tecnico-em-Multimeitos-Didáticos', 'Tecnico-em-Merenda-Escolar',
            'Auxiliar-de-Classe', 'Servente-de-limpeza', 'Monitor-de-Informática', 'Merendeira',
            'Porteiro', 'Estagiário'
        ]
        Cargo.objects.bulk_create([Cargo(nome=n) for n in cargos])

    # Cria os registros Etnia se não existirem
    if not Etnia.objects.exists():
        etnias = ['Branca', 'Negra', 'Parda', 'Amarela', 'Indigena', 'Não declarado']
        Etnia.objects.bulk_create([Etnia(nome=etnia) for etnia in etnias])

    # Cria os registros Nacionalidade se não existirem
    if not Nacionalidade.objects.exists():
        nacionalidades = ['Brasileira', 'Brasileiro nascido no exterior', 'Mexicano']
        Nacionalidade.objects.bulk_create([Nacionalidade(nome=nacionalidade) for nacionalidade in nacionalidades])

    # Cria os registros Pais_origem se não existirem
    if not Pais_origem.objects.exists():
        paises = ['Brasil', 'Japão', 'México']
        Pais_origem.objects.bulk_create([Pais_origem(nome=pais) for pais in paises])

    # Cria os registros Deficiencia_aluno se não existirem
    if not Deficiencia_aluno.objects.exists():
        deficiencias = ['Física', 'Mental', 'Auditiva', 'Visual', 'Nenhuma']
        Deficiencia_aluno.objects.bulk_create([Deficiencia_aluno(nome=deficiencia) for deficiencia in deficiencias])

    # Cria os registros Disciplina se não existirem
    if not Disciplina.objects.exists():
        disciplinas = [
            ('Língua Portuguesa', 1), ('Língua Inglesa', 2), ('Matemática', 3), ('Ciências', 4),
            ('Geografia', 5), ('História', 6), ('Educação Ambiental', 7), ('Educação Artística', 8),
            ('Educação Física', 9)
        ]
        Disciplina.objects.bulk_create([Disciplina(nome=nome, ordem_historico=ordem) for nome, ordem in disciplinas])

    # Cria os registros Compatibilidade_EducaCenso se não existirem
    if not Compatibilidade_EducaCenso.objects.exists():
        areas = [
            'Ensino Fundamental de 9 anos - 1ºano', 'Ensino Fundamental de 9 anos - 2ºano',
            'Ensino Fundamental de 9 anos - 3ºano', 'Ensino Fundamental de 9 anos - 4ºano',
            'Ensino Fundamental de 9 anos - 5ºano', 'Ensino Fundamental de 9 anos - 6ºano',
            'Ensino Fundamental de 9 anos - 7ºano', 'Ensino Fundamental de 9 anos - 8ºano',
            'Ensino Fundamental de 9 anos - 9ºano', 'EJA - Ensino Fundamental - Anos Iniciais',
            'EJA - Ensino Fundamental - Anos Finais', 'Educação Infantil'
        ]
        Compatibilidade_EducaCenso.objects.bulk_create([Compatibilidade_EducaCenso(nome=area) for area in areas])

    # Cria os registros GrauEscolar se não existirem
    if not GrauEscolar.objects.exists():
        graus = ['Ensino Fundamental', 'Ensino Infantil']
        GrauEscolar.objects.bulk_create([GrauEscolar(nome=grau) for grau in graus])

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

    # Cria o registro Cursos se não existir
    if not Cursos.objects.exists():
        Cursos.objects.create(nome="Licenciatura em Pedagogia", nivel=2)

    # Cria o registro Faculdades_ou_Escolas se não existir
    if not Faculdades_ou_Escolas.objects.exists():
        Faculdades_ou_Escolas.objects.create(nome="UNEB - Universidade Estadual da Bahia")

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

    # Cria os registros DiaSemana se não existirem
    if not DiaSemana.objects.exists():
        dias_da_semana = [
            (1, 'Segunda-feira'), (2, 'Terça-feira'), (3, 'Quarta-feira'), (4, 'Quinta-feira'),
            (5, 'Sexta-feira'), (6, 'Sábado'), (7, 'Domingo')
        ]
        DiaSemana.objects.bulk_create([DiaSemana(numero_dia=num, nome_dia=nome) for num, nome in dias_da_semana])
