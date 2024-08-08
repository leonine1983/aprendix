from django.db import models
from datetime import timedelta, date
from django.dispatch import receiver
from django.db.models.signals import post_migrate
from django.core.exceptions import ValidationError


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


class Ano(models.Model):
    ano = models.CharField(max_length=4, null=False, verbose_name='Ano', default='2023')

    def __str__(self):
        return self.ano   


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
    sobrenome = models.CharField(max_length=30, null=False, verbose_name='Sobrenome')    
    sexo = models.ForeignKey(Sexo, models.CASCADE, null=True)
    data_nascimento = models.DateField(null=True)    
    idade= models.CharField(max_length=9, null=True, blank=True)
    nome_profissao = models.ManyToManyField(Profissao, blank=True, verbose_name='Profissões')    
    cpf = models.CharField(max_length=30, null=True, verbose_name='CPF')
    rg= models.CharField(max_length=30, null=True, verbose_name='RG')
    rua= models.CharField(max_length=50, null=True, verbose_name='Nome da rua, avenida etc.')
    complemento= models.CharField(max_length=30, null=True, verbose_name='casa, apartamento etc.')
    numero_casa= models.CharField(max_length=10, null=True, verbose_name='Numero da casa ou s/n')
    bairro = models.ForeignKey(Bairro, on_delete=models.CASCADE, related_name='pessoas_bairro_related', null=True, verbose_name='Bairro')     
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE, related_name='pessoas_cidade_related', null=True, verbose_name='Cidade')
    cep= models.CharField(max_length=30, null=True, verbose_name='CEP')       

    def calcula_idade (self):
        if self.data_nascimento:
            hoje = date.today()
            delta = hoje - self.data_nascimento
            anos = delta.days // 365
            return str(anos) + " anos"
        else:
            return None
        
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
    
    
class Escola(models.Model):
    prefeitura = models.ForeignKey(Prefeitura, on_delete=models.PROTECT, default='', verbose_name='Nome da Instituição Responsável')
    nome_escola = models.CharField(max_length=60, null=False, default='', verbose_name='Nome da Escola ou Departamento')
    endereco_escola = models.CharField(max_length=100, null=False, default='', verbose_name='Endereço')
    telefone_escola = models.CharField(max_length=30, null=True, default='', verbose_name='Telefone')
    # diretor
    # vice_diretor
    # coordenador1
    # coordenador1_turno
    # coordenador2
    # coordenador2_turno
    # coordenador3
    # coordenador3_turno
    # secretario
    def __str__(self):
        return self.nome_escola
    

# Vinculo empregatício --------------------------------------------------------------------------
choice_vinculo = {
    ("contrato" , "Contrato"),
    ("decreto" , "Decreto"),
    ("efetivo" , "efetivo"),
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
    text_contrato = models.ForeignKey(Texto_Contrato,related_name='Texto_contrao_related', null=True, verbose_name='Vinculo com o tipo de contrato', on_delete=models.CASCADE)    
    nome_profissao = models.ForeignKey(Profissao, null=True, verbose_name='Função que irá desempenhar na escola', on_delete=models.CASCADE)     
    nome_escola = models.ForeignKey(Escola, null=True, verbose_name='Escola que o profissional irá desempenhar suas funções', on_delete=models.CASCADE) 
    salario = models.ForeignKey(Salario, null=True, verbose_name='Valor do salário para o cargo escolhido. Atente-se para o ano em que o valor do salário está vigente', on_delete=models.CASCADE)
    data_inicio_contrato = models.DateField(auto_now_add=True)
    data_fim_contrato = models.DateField(null=True)
    tempo_meses = models.IntegerField( null=True)

    def calcula_data_fim_contrato(self):
        if self.tempo_meses and self.data_inicio_contrato:
            # Se os campos tempo_mese e data_inicio_contrato for adicionado pelo usuario
            self.data_fim_contrato = self.data_inicio_contrato + timedelta(days=self.tempo_meses * 30)

    def save(self, *args, **kwargs):
        self.calcula_data_fim_contrato()
        super().save(*args, **kwargs)

    class Meta :
        ordering = ['ano_contrato']

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


    
class Decreto(models.Model):
    profissional = models.ForeignKey(Pessoas, related_name='decreto_profissional', verbose_name='Profissional em que foi emitido o decreto', on_delete=models.CASCADE)
    destino = models.OneToOneField(Escola, related_name='local_decreto', null=False, verbose_name='Local onde o profissional será encaminhado', on_delete=models.CASCADE)
    profissao = models.ForeignKey(Profissao, null=False, verbose_name="Atividade a ser realizada pelo profissional", on_delete=models.CASCADE)
    ano_decreto = models.ForeignKey(Ano, on_delete=models.CASCADE, related_name='Ano_decreto', verbose_name="Ano do")   

    def __str__(self):
        return self.profissional.nome


class Encaminhamentos(models.Model):
    encaminhamento = models.ForeignKey(Contrato, related_name='encaminhamento_escolar', verbose_name='Profissional a ser encaminhado', on_delete=models.CASCADE)
    destino = models.ForeignKey(Escola, related_name='local_encaminhamento', null=False, verbose_name='Local onde o profissional será encaminhado', on_delete=models.CASCADE)
    profissao = models.ForeignKey(Profissao, null=False, verbose_name="Atividade a ser realizada pelo profissional", on_delete=models.CASCADE)

    def __str__(self):
        return self.encaminhamento.contratado.nome  

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


class Frequencia_mes(models.Model):
    ano = models.ForeignKey(Ano, null=False, related_name='frequencia_ano', on_delete=models.CASCADE)
    mes = models.CharField(max_length=30, null=False, verbose_name='Mês')
    local = models.ForeignKey(Escola, related_name='local_frequencia', null=True, verbose_name='Local onde o profissional será encaminhado', on_delete=models.CASCADE)
    profissao = models.ForeignKey(Profissao, null=True,related_name='frequencia_profissional', verbose_name="Frequência do profissional", on_delete=models.CASCADE)

    def __str__(self):
        return self.mes   

# REGISTROS INICIAS ------------------------------------------
@receiver(post_migrate)
def post_migrate_setup(sender, **kwargs):
    if sender.name != 'rh':  # Substitua 'rh' pelo nome do seu app
        return

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
            Cidade.objects.create(nome_estado=uf_unidade_federativa, nome_cidade="Vera Cruz")
        except Uf_Unidade_Federativa.DoesNotExist:
            print("UF Unidade Federativa com ID 5 não encontrada.")

    if not Bairro.objects.exists():
        try:
            cidade = Cidade.objects.get(id=1)
            Bairro.objects.create(nome_cidade=cidade, nome_bairro="Coroa")
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
            ('Professor', 'Profissional dedicado à educação e ao ensino, desempenhando um papel fundamental na transmissão de conhecimentos, habilidades e valores para os alunos.'),
            ('Coordenador Escolar', 'Profissional que supervisiona as operações e as atividades educacionais de uma escola.'),
            ('Merendeira', 'Funcionária responsável pela preparação e distribuição das refeições escolares.'),
            ('Técnica em alimentação escolar', 'Profissional especializada em planejar, preparar e supervisionar refeições nutritivas e balanceadas.'),
            ('Porteiro escolar', 'Profissional encarregado de monitorar e controlar o acesso à escola.'),
            ('Secretária escolar', 'Profissional responsável por tarefas administrativas e organizacionais dentro de uma instituição de ensino.'),
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
    if not Escola.objects.exists():
        prefeitura = Prefeitura.objects.all().first()
        escolas = [
            (prefeitura, "Escola Municipal Geralda Maria", "Endereço 01", "(71) 9 86881943"),
            (prefeitura, "Colégio Municipal de Vera Cruz", "Endereço 02", "(71) 9 86881943")
        ]
        Escola.objects.bulk_create(
            [Escola(prefeitura=p, nome_escola=n, endereco_escola=e, telefone_escola=t) for p, n, e, t in escolas]
        )
