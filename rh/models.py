from django.db import models
from datetime import timedelta, date, datetime
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class Config_plataforma(models.Model):
    data = models.DateField(auto_now_add=True)
    rh_Ativo = models.BooleanField(default=False)
    nome_sistema = models.CharField(max_length=100, default='SME Aprendix')
    versao = models.CharField(max_length=10, default='1.0.0')


class Uf_Unidade_Federativa(models.Model):
    sigla = models.CharField(max_length=2)
    estado = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.estado}/{self.sigla}' 

    
class Cidade(models.Model):
    nome_estado = models.ForeignKey(Uf_Unidade_Federativa, on_delete=models.CASCADE)
    nome_cidade = models.CharField(max_length=30)

    def __str__(self) -> str:
        return self.nome_cidade 
    

class Bairro(models.Model):    
    nome_cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE)
    nome_bairro = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f'{self.nome_bairro}, {self.nome_cidade}'  
    

class Prefeitura(models.Model):
    nome = models.CharField(
        max_length=100,
        verbose_name="Nome da Prefeitura",
        default='Prefeitura'
    )
    instituto = models.CharField(
        max_length=100,
        verbose_name="Instituição",
        default='Nome da Instituição'
    )
    cidade = models.ForeignKey(
        'Cidade',
        on_delete=models.CASCADE,
        related_name="prefeituras",
        null=True,
        blank=True,
        verbose_name="Cidade"
    )
    estado = models.CharField(max_length=100)
    estado = models.ForeignKey(
        'Uf_Unidade_Federativa',
        on_delete=models.CASCADE,
        related_name="prefeituras",
        null=True,
        blank=True,
        verbose_name="Estado"
    )
    endereco = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="Endereço"
    )
    pessoa_publica = models.CharField(
        max_length=100,
        verbose_name="Pessoa Pública Responsável",
        default=''
    )
    brasao = models.ImageField(
        upload_to='brasoes/',
        null=True,
        blank=True,
        verbose_name="Brasão da Prefeitura"
    )

    class Meta:
        verbose_name = "Prefeitura"
        verbose_name_plural = "Prefeituras"
        ordering = ['instituto']

    def __str__(self):
        return f"{self.instituto} - {self.nome}"


class Ano(models.Model):
    prefeitura = models.ForeignKey(Prefeitura, 
                                   related_name='prefeitura_ano_related', 
                                   on_delete=models.PROTECT, 
                                   verbose_name='Escolha a prefeitura à qual sua escola está vinculada',         
                                   null=True,  
                                   blank=True,
        )
    ano = models.CharField(max_length=4, null=False, verbose_name='Digite o ano', default='2025')
    data_inicio = models.DateField(blank=True, null=True, verbose_name="Data de início do ano letivo")
    data_fim = models.DateField(blank=True, null=True, verbose_name="Data de final de ano letivo")       

    class Meta:
        ordering = ['-ano']

    def __str__(self):
        return self.ano

    def save(self, *args, **kwargs):
        # Lógica para criar o próximo ano após 31 de outubro
        if not self.pk:  # Verifica se é um novo objeto (não salvo ainda)
            # Se for o primeiro objeto, defina a data de início como 01/01/2023 e fim como 31/12/2023
            if not self.ano:
                self.ano = str(date.today().year)

            if not self.data_inicio and not self.data_fim:
                # Define a data de início como 01/01 e a data de fim como 31/12
                self.data_inicio = date(int(self.ano), 1, 1)
                self.data_fim = date(int(self.ano), 12, 31)
        
        super(Ano, self).save(*args, **kwargs)  # Salva normalmente após a validação

        # Lógica para criar o próximo ano se for após 31 de outubro
        if self.data_fim and self.data_fim.month == 10 and self.data_fim.day == 31:
            proximo_ano = str(int(self.ano) + 1)
            if not Ano.objects.filter(ano=proximo_ano).exists():  # Verifica se o próximo ano já existe
                Ano.objects.create(
                    ano=proximo_ano,
                    data_inicio=date(int(proximo_ano), 1, 1),
                    data_fim=date(int(proximo_ano), 12, 31)
                )


class Profissao(models.Model):
    nome_profissao = models.CharField(max_length=100, null=False, verbose_name='Profissão')
    descricao = models.TextField(max_length=500, null=False, verbose_name='Descreva a profissão')  

    def __str__(self):
        return self.nome_profissao
    

class Salario(models.Model):
    ano = models.ForeignKey(Ano, null=True,verbose_name='Ano em que o valor do salário está vigente', on_delete=models.CASCADE)
    profissao = models.ForeignKey(Profissao, null=True, verbose_name='Profissão atendida pelo valor do salário', on_delete=models.CASCADE)
    cargaHoraria = models.IntegerField(null=True, verbose_name='Carga horária para o valor vigente')
    valor = models.CharField(max_length=100, null=True, verbose_name='Valor do salário')

    def __str__(self):
        return self.valor


class Sexo(models.Model):
    nome = models.CharField(max_length=30)
    def __str__(self):
        return self.nome
    
   
class Pessoas(models.Model):
    nome = models.CharField(max_length=30, null=False, verbose_name='Nome')
    foto = models.ImageField(upload_to='pessoa_fotos/', null=True, blank=True, verbose_name="Adicione uma foto")
    sobrenome = models.CharField(max_length=30, null=False, verbose_name='Sobrenome')   
    email = models.EmailField(max_length=100, null=True) 
    sexo = models.ForeignKey(Sexo, models.CASCADE, null=True)
    data_nascimento = models.DateField(null=True)    
    idade= models.CharField(max_length=9, null=True, blank=True)
    nome_profissao = models.ForeignKey(Profissao, null=True, blank=True, verbose_name='Profissão', on_delete=models.CASCADE)    
    cpf = models.CharField(max_length=30, null=True, verbose_name='CPF')
    rg= models.CharField(max_length=30, null=True, verbose_name='RG')     
    estado= models.ForeignKey(Uf_Unidade_Federativa, null=True, blank=True, verbose_name='Estado', on_delete=models.CASCADE)    
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE, related_name='pessoas_cidade_related', null=True, verbose_name='Cidade')
    bairro = models.ForeignKey(Bairro, on_delete=models.CASCADE, related_name='pessoas_bairro_related', null=True, verbose_name='Bairro')  
    rua= models.CharField(max_length=50, null=True, verbose_name='Nome da rua, avenida etc.')
    complemento= models.CharField(max_length=30, null=True, verbose_name='casa, apartamento etc.')
    numero_casa= models.CharField(max_length=10, null=True, verbose_name='Numero da casa ou s/n')     
    cep= models.CharField(max_length=30, null=True, verbose_name='CEP')      

    login_professor = models.CharField(max_length=10, null=True, blank=True)     
    senha = models.CharField(max_length=10, null=True, blank=True, default='12345678') 
    profissional_efetivo_no_municipio = models.BooleanField(
        default=False,
        verbose_name="Profissional efetivo no município",
        help_text="Marque se a pessoa for concursada ou efetivada no serviço público municipal."
    )

    def calcula_idade (self):
        if self.data_nascimento:
            hoje = date.today()
            delta = hoje - self.data_nascimento
            anos = delta.days // 365
            return str(anos) + " anos"
        else:
            return None
        
    print("Pessoa")
        
    """
    Função e_aniversario_hoje:
    determinar se a data de nascimento de uma pessoa coincide
     com a data atual, ou seja, se hoje é o aniversário dessa pessoa.
    """  
    def e_aniversario_hoje(self):
        hoje = datetime.now().date()
        return (self.data_nascimento and 
                self.data_nascimento.month == hoje.month and 
                self.data_nascimento.day == hoje.day)
        
    def save(self, *args, **kwargs):
        self.idade = self.calcula_idade()
        existing_pessoas = Pessoas.objects.filter(
            nome = self.nome,
            cpf = self.cpf,
            rg = self.rg,            
        )
        if self.pk:
            existing_pessoas = existing_pessoas.exclude(pk = self.pk)
        # Se existir uma pessoa com as mesmas informações, gere um aviso
        if existing_pessoas.exists():
            raise ValidationError ("Já existe um registro com essas informações")
        super(Pessoas, self).save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.nome} {self.sobrenome}'  


CHOICES = [
    ('professor', 'Professor'),
    ('funcionario', 'Funcionário'),
    ('estagio', 'Estágio'),
    ('voluntario', 'Voluntário')
]


class Texto_Contrato(models.Model):
    tipo = models.CharField(max_length=20, choices=CHOICES)
    # texto = RichTextField(blank=True, null=True)
    texto = models.TextField(max_length=2000, null=True, blank=True)   

    def __str__(self):
        return self.tipo
    

class UserPessoas(models.Model):
    """
    Modelo que representa o vínculo entre um usuário do sistema (User) 
    e um registro de pessoa (Pessoas).

    Esse relacionamento é um-para-um, garantindo que cada usuário 
    esteja associado a uma única pessoa e vice-versa.
    """ 
    user = models.OneToOneField(User, related_name="related_vinculoUserPessoa", on_delete=models.CASCADE)
    pessoa = models.OneToOneField(Pessoas, related_name="related_vinculoPessoaUser", on_delete=models.PROTECT)

    def __str__(self) :
        return f'{self.pessoa.nome} {self.pessoa.sobrenome}'
    

class Escola(models.Model):
    prefeitura = models.ForeignKey(Prefeitura, on_delete=models.PROTECT, verbose_name='Nome da Instituição Responsável')
    nome_escola = models.CharField(max_length=60, verbose_name='Nome da Escola ou Departamento')
    sigla_escola = models.CharField(max_length=60, verbose_name='Sigla da escola', null=True)
    endereco_escola = models.CharField(max_length=100, null=True, blank=True, verbose_name='Endereço')
    telefone_escola = models.CharField(max_length=30, null=True, blank=True, verbose_name='Telefone')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')    
    author_created = models.CharField(max_length=50, null=True, blank=True, verbose_name='Autor da criação')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Data da Última Atualização')
    author_atualiza = models.CharField(max_length=50, null=True, blank=True, verbose_name='Autor da atualização')
    fund2 = models.BooleanField(default=False, verbose_name="Escola de séries finais")

    class Meta:
        ordering = ['-fund2','nome_escola']

    def __str__(self):
        return self.nome_escola
    
    
class EscolaUser(models.Model):
    escola = models.ForeignKey(Escola, on_delete=models.CASCADE, verbose_name="Escola em que o usuário estará vinculado", related_name="related_escolaUser")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Nome do Usuário", related_name="related_UserEscola" )
    superuser = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.escola.nome_escola}"
    

# Vinculo empregatício --------------------------------------------------------------------------
choice_vinculo = {
    ("contrato" , "Contrato"),
    ("estagio" , "estagio"),
}

class Vinculo_empregaticio(models.Model):
    pessoa = models.ForeignKey(Pessoas, on_delete=models.CASCADE, null=True)
    vinculo = models.CharField(max_length=10, choices=choice_vinculo, null=True)
    ano = models.ForeignKey(Ano, on_delete=models.CASCADE, null=True)

    def __str__(self) :
        return self.pessoa.nome


class Contrato(models.Model):
    ano_contrato = models.ForeignKey(Ano, related_name='ano_contrato_related',verbose_name='Ano do contrato', on_delete=models.CASCADE)
    contratado = models.ForeignKey(Pessoas, related_name='pessoa_contratada', verbose_name='Pessoa a ser contratada', on_delete=models.CASCADE)
    text_contrato = models.ForeignKey(Texto_Contrato,related_name='Texto_contrao_related', null=True, blank=True, verbose_name='Vinculo com o tipo de contrato', on_delete=models.CASCADE)    
    nome_profissao = models.ForeignKey(Profissao, null=True, verbose_name='Função que irá desempenhar na escola', on_delete=models.CASCADE)     
    nome_escola = models.ForeignKey(Escola, null=True, verbose_name='Escola que o profissional irá desempenhar suas funções', on_delete=models.CASCADE) 
    salario = models.ForeignKey(Salario, null=True, blank=True, verbose_name='Valor do salário para o cargo escolhido. Atente-se para o ano em que o valor do salário está vigente', on_delete=models.CASCADE)
    data_inicio_contrato = models.DateField(auto_now_add=True)
    data_fim_contrato = models.DateField(null=True, blank=True)
    tempo_meses = models.IntegerField( null=True, blank=True)

    #Segurança
    created = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')    
    author_created = models.CharField(max_length=50, null=True, blank=True, verbose_name='Autor da criação')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Data da Última Atualização')
    author_atualiza = models.CharField(max_length=50, null=True, blank=True, verbose_name='Autor da atualização')

    def calcula_data_fim_contrato(self):
        if self.tempo_meses and self.data_inicio_contrato:
            # Se os campos tempo_mese e data_inicio_contrato for adicionado pelo usuario
            self.data_fim_contrato = self.data_inicio_contrato + timedelta(days=self.tempo_meses * 30)

    def save(self, *args, **kwargs):
        self.calcula_data_fim_contrato()
        super().save(*args, **kwargs)

    class Meta :
        ordering = ['-ano_contrato']

    def __str__(self):
        return str(self.contratado)

    # Sobrescreve o método save para verifique se já existe algum registros com as informações fornecidas pelo usuario
    def save(self, *args, **kwargs):
        # Verifica se já existe um contrato com as mesmas informações
        existing_contracts = Contrato.objects.filter(
            contratado = self.contratado,
            nome_escola= self.nome_escola,
            ano_contrato = self.ano_contrato
        )
        
        # Exclua o contrato da atual consulta, se estiver atualizando
        if self.pk:
            existing_contracts = existing_contracts.exclude(pk=self.pk)
        # Se já existir um contrato com as mesmas informações, gere um aviso
        if existing_contracts.exists():
            raise ValidationError ("Já existe contrato com as mesmas informações")

        # Se não existir um contrato com as mesmas informações, continue salvando
        super().save(*args, **kwargs)


class ProfEfetivo(models.Model):
    pessoa = models.ForeignKey(Pessoas, related_name='pessoa_efetiva', verbose_name='Pessoa efetiva', on_delete=models.CASCADE)    
    matricula = models.CharField("Matrícula funcional", max_length=20, unique=True)
    cargo = models.CharField("Cargo", max_length=100)
    funcao = models.CharField("Função exercida", max_length=100, blank=True, null=True)
    data_ingresso = models.DateField("Data de ingresso no município")
    data_posse = models.DateField("Data de posse no cargo", blank=True, null=True)
    regime_trabalho = models.CharField(
        "Regime de trabalho",
        max_length=30,
        choices=[('20h', '20h'), ('30h', '30h'), ('40h', '40h')],
        default='40h'
    )
    situacao = models.CharField(
        "Situação funcional",
        max_length=20,
        choices=[('ativo', 'Ativo'), ('afastado', 'Afastado'), ('aposentado', 'Aposentado')],
        default='ativo'
    )
    escola_lotacao = models.ForeignKey( Escola, related_name='profissionais_efetivos',
        verbose_name='Unidade de lotação',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    observacoes = models.TextField("Observações", blank=True, null=True)

    class Meta:
        verbose_name = "Profissional Efetivo"
        verbose_name_plural = "Profissionais Efetivos"

    def __str__(self):
        return f"{self.pessoa.nome_completo} ({self.matricula})"
    
    
class Decreto(models.Model):
    profissional = models.ForeignKey(Pessoas, related_name='decreto_profissional', verbose_name='Profissional em que foi emitido o decreto', on_delete=models.CASCADE)
    destino = models.ForeignKey(Escola, related_name='local_decreto', null=False, verbose_name='Local onde o profissional será encaminhado', on_delete=models.CASCADE)
    profissao = models.ForeignKey(Profissao, null=False, verbose_name="Atividade a ser realizada pelo profissional", on_delete=models.CASCADE)
    ano_decreto = models.ForeignKey(Ano, on_delete=models.CASCADE, related_name='Ano_decreto', verbose_name="Ano de Publicação do Decreto")   
    numero_decreto = models.CharField(max_length=50,  null=False,  verbose_name='Número de controle do decreto')

    #Segurança
    created = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')    
    author_created = models.CharField(max_length=50,  null=True, blank=True, verbose_name='Autor da criação')
    atualizado_em = models.DateTimeField(auto_now=True,  verbose_name='Data da Última Atualização')
    author_atualiza = models.CharField(max_length=50, null=True, blank=True, verbose_name='Autor da atualização')

    def __str__(self):
        return f'{self.profissional}, Decreto n° {self.numero_decreto}/{self.ano_decreto}'
    

class DecretoAnoLetivoAtivo(models.Model):
    decreto = models.ForeignKey(Decreto, on_delete=models.CASCADE, related_name='Decreto_decretoAtivo', verbose_name="Definir se o decreto está ativo para o ano letivo atual")  
    ano_ativo = models.ForeignKey(Ano, on_delete=models.CASCADE, related_name='Ano_decretoAtivo', verbose_name="Definir se o decreto está ativo para o ano letivo atual")  
   
    #Segurança
    created = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')    
    author_created = models.CharField(max_length=50,  null=True, blank=True, verbose_name='Autor da criação')
    atualizado_em = models.DateTimeField(auto_now=True,  verbose_name='Data da Última Atualização')
    author_atualiza = models.CharField(max_length=50, null=True, blank=True, verbose_name='Autor da atualização')

    def __str__(self):
        return f'Em atividade para {self.ano_ativo}'


class Escola_admin(models.Model):
    # Dados Gerais
    nome = models.OneToOneField(Escola, related_name="related_dadosEscola", on_delete=models.CASCADE, blank=True, null=True)
    imagem = models.ImageField(upload_to='escolas/', blank=True, null=True)
    cnpj = models.CharField(max_length=14, blank=True, null=True, unique=True)  # CNPJ no formato XXX.XXX.XXX/0001-XX
    endereco = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.ForeignKey(Bairro, related_name="related_dadosEscola_bairro", on_delete=models.CASCADE, blank=True, null=True)
    bairro_atendEscola= models.ManyToManyField(Bairro, related_name="related_bairroAtend1", verbose_name="Outros bairros que são atendidos pela escola", blank=True)
    cidade = models.ForeignKey(Cidade, related_name="related_dadosEscola_cidade", on_delete=models.CASCADE, blank=True, null=True)
    estado = models.ForeignKey(Uf_Unidade_Federativa, related_name="related_UF_escola", on_delete=models.CASCADE, blank=True, null=True)
    cep = models.CharField(max_length=8, blank=True, null=True)  # CEP no formato XXXXX-XXX
    telefone = models.CharField(max_length=15, blank=True, null=True)  # Telefone com DDD
    email = models.EmailField(blank=True, null=True)
    
    # Dados de Identificação
    codigo_mec = models.CharField(max_length=10, blank=True, null=True, unique=True)  # Código do MEC
    tipo = models.CharField(max_length=50, blank=True, null=True)  # Ex.: 'Pública', 'Privada', 'Filantrópica'
    
    """
    O acesso a diretores e secretarios e outros decretos e feito pelo model Decretos
    # Dados de Direção
    nome_diretor = models.ForeignKey(Decreto, related_name="related_dadosEscola_decreto_diretor", on_delete=models.CASCADE, blank=True, null=True)
    nome_secretario = models.ForeignKey(Decreto, related_name="related_dadosEscola_decreto_secretaria", on_delete=models.CASCADE, blank=True, null=True)
    nome_vice_diretor_matutino = models.ForeignKey(Decreto, related_name="related_dadosEscola_decreto_Vicediretor_matutino", verbose_name='Vice Diretor Matutino', on_delete=models.CASCADE, blank=True, null=True)
    nome_vice_diretor_vespertino = models.ForeignKey(Decreto, related_name="related_dadosEscola_decreto_Vicediretor_vespertino",verbose_name='Vice Diretor Vespertino', on_delete=models.CASCADE, blank=True, null=True)
    nome_vice_diretor_Noturno = models.ForeignKey(Decreto, related_name="related_dadosEscola_decreto_Vicediretor_noturno",verbose_name='Vice Diretor Noturno', on_delete=models.CASCADE, blank=True, null=True)

    # Dados de Coordenação por Turno
    coordenacao_matutino = models.ForeignKey(Decreto, related_name="related_dadosEscola_decreto_coordMat", on_delete=models.CASCADE, blank=True, null=True)
    coordenacao_vespertino = models.ForeignKey(Decreto, related_name="related_dadosEscola_decreto_coordVesp", on_delete=models.CASCADE, blank=True, null=True)
    coordenacao_noturno = models.ForeignKey(Decreto, related_name="related_dadosEscola_decreto_coordNot", on_delete=models.CASCADE, blank=True, null=True)
    """

    # Dados de Funcionamento
    data_fundacao = models.DateField(blank=True, null=True)
    turno = models.CharField(max_length=50, blank=True, null=True)  # Ex.: 'Matutino', 'Vespertino', 'Noturno'
    num_alunos = models.PositiveIntegerField(blank=True, null=True)
    num_funcionarios_n_docente = models.PositiveIntegerField(blank=True, null=True)
    num_funcionarios_docente = models.PositiveIntegerField(blank=True, null=True)
    num_funcionarios_total = models.PositiveIntegerField(blank=True, null=True)
    numero_turmas = models.PositiveIntegerField(blank=True, null=True)
    
    # Dados da Infraestrutura
    qtd_salas = models.PositiveIntegerField(blank=True, null=True)
    qtd_bibliotecas = models.PositiveIntegerField(default=0, blank=True, null=True)
    qtd_laboratorios = models.PositiveIntegerField(default=0, blank=True, null=True)
    qtd_quadras = models.PositiveIntegerField(default=0, blank=True, null=True)
    qtd_auditorios = models.PositiveIntegerField(default=0, blank=True, null=True)
    qtd_refeitórios = models.PositiveIntegerField(default=0, blank=True, null=True)
    qtd_areas_verdes = models.PositiveIntegerField(default=0, blank=True, null=True)

    # Dados de Curso
    possui_educacao_infantil = models.BooleanField(default=False, blank=True, null=True)
    possui_ensino_fundamental = models.BooleanField(default=False, blank=True, null=True)
    possui_ensino_medio = models.BooleanField(default=False, blank=True, null=True)
    possui_ensino_tecnico = models.BooleanField(default=False, blank=True, null=True)
    
    # Dados de Convênios e Parcerias
    convenios = models.TextField(blank=True, null=True)
        
    # Dados de Segurança e Acessibilidade
    possui_acessibilidade = models.BooleanField(default=False, blank=True, null=True)
    possui_sistema_seguranca = models.BooleanField(default=False, blank=True, null=True)    
    
    # Outros Campos
    observacoes = models.TextField(blank=True, null=True)

    #Segurança
    created = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')    
    author_created = models.CharField(max_length=50, null=True, blank=True, verbose_name='Autor da criação')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Data da Última Atualização')
    author_atualiza = models.CharField(max_length=50, null=True, blank=True, verbose_name='Autor da atualização')

    escola_dados_ok = models.BooleanField(default=False)
    
    def __str__(self):
        return self.nome.nome_escola


class Encaminhamentos(models.Model):
    encaminhamento = models.ForeignKey(Contrato, related_name='encaminhamento_escolar', verbose_name='Profissional a ser encaminhado', on_delete=models.CASCADE)        
    destino = models.ForeignKey(Escola, related_name='local_encaminhamento', null=False, verbose_name='Local onde o profissional será encaminhado', on_delete=models.CASCADE)
    profissao = models.ForeignKey(Profissao, null=False, verbose_name="Atividade a ser realizada pelo profissional", on_delete=models.CASCADE)

    #Segurança
    created = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')    
    author_created = models.CharField(max_length=50, null=True, blank=True, verbose_name='Autor da criação')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Data da Última Atualização')
    author_atualiza = models.CharField(max_length=50, null=True, blank=True, verbose_name='Autor da atualização')

    def __str__(self):
        return f'{self.encaminhamento.contratado.nome} {self.encaminhamento.contratado.sobrenome} - RG nº {self.encaminhamento.contratado.rg}'  

    def save(self, *args, **kwargs):
        # Verifica se já existe um contrato com as mesmas informações
        existing_encaminhaments = Encaminhamentos.objects.filter(
            encaminhamento = self.encaminhamento,
            destino = self.destino,
            profissao = self.profissao            
        )

        # Exclua o contrato da atual consulta, se estiver atualizando
        if self.pk:
            existing_encaminhaments = existing_encaminhaments.exclude(pk = self.pk)
        # Se já existir um contrato com as mesmas informações, gere um aviso
        if existing_encaminhaments.exists():
            raise ValidationError ("Já existe contrato com as mesmas informações")

        # Se não existir um contrato com as mesmas informações, continue salvando
        super().save(*args, **kwargs)


class Feriado(models.Model):
    data = models.DateField(unique=True)
    nome = models.CharField(max_length=100)
    local = models.BooleanField(default=False)  # Para indicar se é um feriado local

    def __str__(self):
        return self.nome


class Frequencia_mes(models.Model):
    ano = models.ForeignKey(Ano, null=False, related_name='frequencia_ano', on_delete=models.CASCADE)
    mes = models.CharField(max_length=30, null=False, verbose_name='Mês')
    local = models.ForeignKey(Escola, related_name='local_frequencia', null=True, verbose_name='Local onde o profissional será encaminhado', on_delete=models.CASCADE)
    profissao = models.ForeignKey(Profissao, null=True,related_name='frequencia_profissional', verbose_name="Frequência do profissional", on_delete=models.CASCADE)

    #Segurança
    created = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')    
    author_created = models.CharField(max_length=50, null=True, blank=True, verbose_name='Autor da criação')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Data da Última Atualização')
    author_atualiza = models.CharField(max_length=50, null=True, blank=True, verbose_name='Autor da atualização')

    def __str__(self):
        return self.mes   
    