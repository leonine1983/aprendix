from django.db import models
from datetime import timedelta, date, datetime
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_migrate
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User



class Config_plataforma(models.Model):
    data = models.DateField(auto_now_add=True)
    rh_Ativo = models.BooleanField(default=False) 


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
    prefeitura_nome = models.CharField(max_length=50, null=False, default='Prefeitura')
    instituto = models.CharField(max_length=50, null=False, default='Nome da Instituição')
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE, related_name="prefeitura_cidade_related", null=True, blank=True)
    estado = models.ForeignKey(Uf_Unidade_Federativa, related_name="prefeitura_estado_related", on_delete=models.CASCADE, null=True, blank=True)
    endereco = models.CharField(max_length=50, null=True, default='')
    pessoa_publica = models.CharField(max_length=30, null=False, default='')

    def __str__(self):
        return self.instituto   


from django.db import models
from datetime import date, timedelta

class Ano(models.Model):
    ano = models.CharField(max_length=4, null=False, verbose_name='Ano', default='2025')
    data_inicio = models.DateField(blank=True, null=True)
    data_fim = models.DateField(blank=True, null=True)       

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
    rua= models.CharField(max_length=50, null=True, verbose_name='Nome da rua, avenida etc.')
    complemento= models.CharField(max_length=30, null=True, verbose_name='casa, apartamento etc.')
    numero_casa= models.CharField(max_length=10, null=True, verbose_name='Numero da casa ou s/n')
    bairro = models.ForeignKey(Bairro, on_delete=models.CASCADE, related_name='pessoas_bairro_related', null=True, verbose_name='Bairro')     
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE, related_name='pessoas_cidade_related', null=True, verbose_name='Cidade')
    cep= models.CharField(max_length=30, null=True, verbose_name='CEP')      

    login_professor = models.CharField(max_length=10, null=True, blank=True)     
    senha = models.CharField(max_length=10, null=True, blank=True, default='12345678') 

    def calcula_idade (self):
        if self.data_nascimento:
            hoje = date.today()
            delta = hoje - self.data_nascimento
            anos = delta.days // 365
            return str(anos) + " anos"
        else:
            return None
        
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

    class Meta:
        ordering = ['nome_escola']

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
    bairro_atendEscola= models.ManyToManyField(Bairro, related_name="related_bairroAtend1", verbose_name="Outros bairros que são atendidos pela escola", blank=True, null=True)
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

# REGISTROS INICIAS ------------------------------------------
@receiver(post_migrate)
def post_migrate_setup(sender, **kwargs):
    if sender.name != 'rh':  # Substitua 'rh' pelo nome do seu app
        return
    
    
    if not Ano.objects.exists():
        try:
            Ano.objects.create(
                ano=2024 
            )
        except Ano.DoesNotExist:
            print("Ano com ID 1 não encontrado.")

    # Cria o registro Config_Plataforma se não existir
    if not Config_plataforma.objects.exists():
        Config_plataforma.objects.create(rh_Ativo=False)
    
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

    # Cria registros Cidade e Bairro se não existirem
    if not Cidade.objects.exists():
        try:
            uf_unidade_federativa = Uf_Unidade_Federativa.objects.get(id=5)

            cidades_bahia = [
                'Abaíra', 'Acajutiba', 'Adustina', 'Água Fria', 'Aiquara', 'Alagoinhas', 'Alcobaça', 'Almadina', 'Amargosa', 
                'Amélia Rodrigues', 'Anagé', 'Andaraí', 'Angical', 'Anguera', 'Antas', 'Antônio Cardoso', 'Antônio Gonçalves', 
                'Aporá', 'Aracatu', 'Araçás', 'Arataca', 'Aratuípe', 'Aurelino Leal', 'Baianópolis', 'Baixa Grande', 'Banzaê', 
                'Barra', 'Barra da Estiva', 'Barra do Choça', 'Barra do Mendes', 'Barro Alto', 'Barrocas', 'Belmonte', 'Belo Campo', 
                'Biritinga', 'Boa Nova', 'Boa Vista do Tupim', 'Bom Jesus da Lapa', 'Bom Jesus da Serra', 'Boninal', 'Bonito', 
                'Boquira', 'Botuporã', 'Brejões', 'Brejolândia', 'Camaçari', 'Camacan', 'Candeias', 'Candido Motta', 'Cansanção', 
                'Capela do Alto Alegre', 'Caraíbas', 'Caravelas', 'Cardeal da Silva', 'Carinhanha', 'Casa Nova', 'Castro Alves', 
                'Catolândia', 'Catu', 'Cícero Dantas', 'Cipó', 'Coaraci', 'Coco', 'Conceição da Feira', 'Conceição do Almeida', 
                'Conde', 'Condeúba', 'Contendas do Sincorá', 'Coração de Maria', 'Crisópolis', 'Cristópolis', 'Cururupe', 'Dário Meira', 
                'Dias d\'Ávila', 'Dom Basílio', 'Dom Macedo Costa', 'Elísio Medrado', 'Encruzilhada', 'Entre Rios', 'Esplanada', 'Euclides da Cunha', 
                'Eunápolis', 'Fátima', 'Feira de Santana', 'Filadélfia', 'Formosa do Rio Preto', 'Gandu', 'Gavião', 'Gentio do Ouro', 'Glória', 
                'Gongogi', 'Governador Mangabeira', 'Guaratinga', 'Heliópolis', 'Ibotirama', 'Icaraí', 'Ichu', 'Igaporã', 'Igrapiúna', 'Iguaí', 
                'Ilhéus', 'Inhambupe', 'Ipecaetá', 'Ipiaú', 'Ipirá', 'Iraquara', 'Irará', 'Irecê', 'Itabela', 'Itaberaba', 'Itabuna', 'Itacaré', 
                'Itaeté', 'Itagi', 'Itagibá', 'Itajuípe', 'Itamaraju', 'Itanagra', 'Itaparica', 'Itapé', 'Itapetinga', 'Itapicuru', 'Itiruçu', 
                'Itororó', 'Ituaçu', 'Ituberá', 'Jacobina', 'Jaguaçu', 'Jaguarari', 'Jandaíra', 'Jequié', 'Jeremoabo', 'Jiquiriçá', 'João Dourado', 
                'Juazeiro', 'Jussara', 'Jussiape', 'Lafaiete Coutinho', 'Lagoa Real', 'Laje', 'Laje do Muriaé', 'Lencóis', 'Licínio de Almeida', 
                'Livramento de Nossa Senhora', 'Luís Eduardo Magalhães', 'Macajuba', 'Macarani', 'Macaúbas', 'Madre de Deus', 'Maetinga', 'Mairi', 
                'Malhada', 'Malhada de Pedras', 'Manoel Vitorino', 'Maracás', 'Maragogipe', 'Maraú', 'Marcionílio Souza', 'Mascote', 'Mata de São João', 
                'Matina', 'Medeiros Neto', 'Miguel Calmon', 'Milagres', 'Mirangaba', 'Morro do Chapéu', 'Mortugaba', 'Mucugê', 'Mucuri', 'Mundo Novo', 
                'Muniz Ferreira', 'Muquém de São Francisco', 'Muritiba', 'Mundo Novo', 'Nazaré', 'Nilo Peçanha', 'Nordestina', 'Nova Canaã', 
                'Nova Fátima', 'Nova Ibiá', 'Nova Itarana', 'Nova Redenção', 'Nova Soure', 'Novo Horizonte', 'Olindina', 'Oliveira dos Brejinhos', 
                'Ourolândia', 'Palmeiras', 'Paramirim', 'Paratinga', 'Paripiranga', 'Pau Brasil', 'Paulo Afonso', 'Pedrão', 'Pedro Alexandre', 'Piatan', 
                'Pilão Arcado', 'Pindaí', 'Pintadas', 'Pojuca', 'Ponto Novo', 'Porto Seguro', 'Potiraguá', 'Prado', 'Presidente Jânio Quadros', 
                'Presidente Tancredo Neves', 'Queimadas', 'Rafael Jambeiro', 'Remanso', 'Retirolândia', 'Riachão das Neves', 'Riachão do Jacuípe', 
                'Ribeira do Pombal', 'Ribeirão do Largo', 'Rio de Contas', 'Rio Real', 'Salinas', 'Salvador', 'Santa Bárbara', 'Santa Brígida', 
                'Santa Cruz Cabrália', 'Santa Cruz da Vitória', 'Santa Inês', 'Santa Luzia', 'Santa Maria da Vitória', 'Santana', 'Santanópolis', 
                'Santo Amaro', 'Santo Estêvão', 'São Desidério', 'São Domingos', 'São Félix', 'São Felipe', 'São Francisco do Conde', 'São Gonçalo do Amarante',
                'São João do Paraíso', 'São José da Vitória', 'São Miguel das Matas', 'São Sebastião do Passé', 'Sapeaçu', 'Santo Antônio de Jesus', 
                'São Sebastião', 'Sítio do Mato', 'Sítio do Quinto', 'Sobradinho', 'Tanhaçu', 'Tanhaípe', 'Teixeira de Freitas', 'Teodoro Sampaio', 
                'Tremedal', 'Tucano', 'Ubaíra', 'Ubatã', 'Uibaí', 'Utinga', 'Valença', 'Valente', 'Várzea da Roça', 'Várzea do Poço', 'Vera Cruz', 
                'Vitória da Conquista'
            ]

            for cidade in cidades_bahia:
                Cidade.objects.create(nome_estado=uf_unidade_federativa, nome_cidade=cidade)         



        except Uf_Unidade_Federativa.DoesNotExist:
            print("UF Unidade Federativa com ID 5 não encontrada.")

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

        except Cidade.DoesNotExist:
            print("Cidade com ID 1 não encontrada.")

    # Cria o registro Prefeitura se não existir
    if not Prefeitura.objects.exists():
        try:
            cidade = Cidade.objects.get(pk=1)
            estado = Uf_Unidade_Federativa.objects.get(pk=1)
            Prefeitura.objects.create(
                prefeitura_nome='Prefeitura Municipal de Algum Lugar',
                instituto='Secretaria Municipal da Educação',
                cidade=cidade,
                estado=estado,
                endereco='Av. Te encontro lá',
                pessoa_publica='Petepan'
            )
        except Cidade.DoesNotExist:
            print("Cidade com PK 1 não encontrada.")
        except Uf_Unidade_Federativa.DoesNotExist:
            print("UF Unidade Federativa com PK 1 não encontrada.")

    # Cria o registro Ano se não existir
    if not Ano.objects.exists():
        Ano.objects.create(ano='2023')

    # Cria registros de Profissao se não existirem
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

    # Cria registros de Sexo se não existirem
    if not Sexo.objects.exists():
        Sexo.objects.bulk_create(
            [Sexo(nome=sexo) for sexo in ['Masculino', 'Feminino']]
        )


    # Cria registros de Escola se não existirem
    # Cria registros de Escola se não existirem
    if not Escola.objects.exists():
        prefeitura = Prefeitura.objects.all().first()
        
        if prefeitura is None:
            print("Nenhuma prefeitura encontrada.")
        else:
            # Definindo as escolas a serem criadas
            escolas = [
                (prefeitura, "Escola Municipal Geralda Maria"),
                (prefeitura, "Colégio Municipal de Vera Cruz")
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
