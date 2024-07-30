from django.db import models
from rh.models import Prefeitura
from rh.models import Escola as Escolas_model
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver 
import random
from django.contrib.auth.models import User
from django.conf import settings

medida = {
        ('kg', 'kg'),
        ('litros', 'litros'),  
    }

escolha = {
    ('entrada' , 'Entrada {Cantina Geral (Estoque)}'),
    ('saida' , 'Saída')
}
    

# FORNECEDOR -------------------------------------------------------------------------------VIEWS--ok
class Fornecedor(models.Model):
    nome = models.CharField(max_length=30, null=False, default='')
    codigo = models.CharField(max_length=8, null=False, unique=True)
    endereco = models.CharField(max_length=50, null=False, default='')
    telefone = models.CharField(max_length=30, null=False, default='')
    cnpj = models.CharField(max_length=18, null=False, default='', verbose_name='CNPJ')
    email = models.CharField(max_length=30, null=False, default='')

    def save(self, *args, **kwargs):
        if not self.codigo:  # Verifica se o código está vazio
            self.codigo = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        unique = False
        while not unique:
            # Gera um novo código aleatório
            new_code = f'{random.randint(0, 9999):05d}-{random.randint(0, 9):02d}'
            # Verifica se já existe um fornecedor com esse código
            if not Fornecedor.objects.filter(codigo=new_code).exists():
                unique = True
        return new_code

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.nome
# -------------------------------------------------------------------------------------END VIEWS----ok


# CATEGORIA ALIMENTO
class Categoria_alimentos(models.Model):
    nome = models.CharField(max_length=30, null=False, default='Nenhuma', verbose_name='Escreva o nome da categoria de alimentos que deseja criar. Ex.: Vegetais')

    def __str__(self):
        return self.nome


# ALIMENTO
class Alimentos(models.Model):
    nome = models.CharField(max_length=30, null=False, default='Nome do alimento')
    prefeitura = models.ForeignKey(Prefeitura, on_delete=models.PROTECT, default='', verbose_name='Nome da Instituição principal')
    categoria_alimento = models.ForeignKey(Categoria_alimentos, on_delete=models.PROTECT, default='')
    quantidade_disponivel = models.PositiveBigIntegerField(default=0)    
    unidade = models.CharField(max_length=10,null=False)      

    class Meta:
        ordering = ['-quantidade_disponivel']


    def __str__(self):
        return self.nome
    

# MOVIMENTAÇÃO DE ESTOQUE
""" 
    O modelo de Movimentação de Estoque serve para registrar e controlar as movimentações de alimentos no estoque.
Ele permite acompanhar todas as entradas e saídas de alimentos, fornecendo informações essenciais para o gerenciamento do estoque.
    Com esse modelo, é possível registrar as operações de entrada de alimentos, como recebimento de mercadorias de fornecedores, 
transferências internas de outros locais de armazenamento ou produção interna de alimentos. 
    Além disso, as operações de saída de alimentos, como distribuição para as escolas ou unidades beneficiárias, 
vendas ou descarte de produtos vencidos, também podem ser registradas.
    Ao utilizar o modelo de Movimentação de Estoque, é possível manter um controle preciso sobre
a quantidade e a disponibilidade de cada alimento no estoque, atualizando os registros conforme 
as movimentações são realizadas. Essas informações são importantes para evitar desperdícios, garantir
a reposição adequada de alimentos, gerenciar prazos de validade e manter um controle eficiente dos recursos disponíveis.
Além disso, o modelo de Movimentação de Estoque pode fornecer dados para análises futuras, como relatórios de fluxo de estoque,
identificação de tendências de demanda, cálculos de rotatividade de estoque e auxílio na tomada de decisões estratégicas 
relacionadas ao gerenciamento de estoque.
    Em resumo, o modelo de Movimentação de Estoque desempenha um papel fundamental no controle e na gestão eficiente dos alimentos,
permitindo o registro e o acompanhamento das movimentações do estoque, contribuindo para a organização e otimização dos recursos disponíveis.
"""
class Movimentacao_Estoque(models.Model):
    tipo = models.CharField(max_length=30, verbose_name='Tipo de movimentação:')
    local_destino = models.ForeignKey(Escolas_model, on_delete=models.PROTECT)
    alimento = models.ForeignKey(Alimentos, on_delete=models.CASCADE) 
    fornecedor_alimento = models.ForeignKey(Fornecedor, on_delete=models.PROTECT)           
    data_hora = models.DateTimeField(auto_now_add=True)     
    quantidade = models.PositiveBigIntegerField(max_length=10)
    numero_nota_fiscal = models.CharField(max_length=9, verbose_name='Nº da nota fiscal', default='000000000')
    unidadeMedida = models.CharField(choices=medida, max_length=10, verbose_name='Unidade de Medida')      
    # Para criar uma relação ForeignKey com o modelo de usuário do Django (User),
    # é recomendado que você utilize o settings.AUTH_USER_MODEL em vez do próprio modelo User. 
    # Isso garante que, caso o modelo de usuário seja personalizado em algum momento, a relação ainda funcionará corretamente.
    responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT) 
    observacoes = models.CharField(max_length=150)    
    #enviado = models.CharField(max_length=3, null=True, default='Não')
    

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Salva a data de validade ja existente
        """
        if not self.data_validade:
            last_record = Movimentacao_Estoque.objects.filter(alimento = self.alimento).last()
            if last_record:
                self.data_validade = last_record.data_validade
        super().save(*args, **kwargs)
        """
        # Atualiza quantidade disponivel do alimento
        # relacionada à movimentação no estoque
        if self.tipo == 'entrada':
            self.alimento.quantidade_disponivel += self.quantidade 
            self.alimento.unidade = self.unidadeMedida
        
        elif self.tipo == 'saida':
            self.alimento.quantidade_disponivel -= self.quantidade
        
        self.alimento.save()

    
    class Meta:
        ordering = ['-data_hora']



    def __str__(self):
        return  self.tipo


# RECEITA

# PROGRAMAÇÃO DE SAIDA DE ESTOQUE
"""
A Programação de Saída de Estoque é responsável por planejar e agendar a entrega de alimentos
para as escolas ou instituições beneficiárias. Ela envolve a definição dos alimentos a serem enviados,
a escola beneficiária e as retiradas de merenda relacionadas."""
class ProgramacaoSaidaEstoque(models.Model):
    movimentacoes_estoque = models.ManyToManyField(Movimentacao_Estoque)
    data_agendamento = models.DateField(auto_created=False) 
    situacao = models.BooleanField(verbose_name='Enviado', null=True)



@receiver(post_migrate)
def cria_registro(sender, **kwargs):
    if not Fornecedor.objects.exists():            
        Fornecedor.objects.create(
            id = 1,
            nome = 'Cantina Geral',
            endereco = 'Precisa Atualizar',
            cnpj = '0000000-0',
            email = 'aaaa@aaa.aaa'

        )

         

"""
class ProgramacaoSaidaEstoque(models.Model):
    alimentos_a_enviar = models.ManyToManyField('Alimento')
    escola_beneficiaria = models.OneToOneField('Escola', on_delete=models.CASCADE)

class RetiradaMerenda(models.Model):
    programacao_saida_estoque = models.ForeignKey('ProgramacaoSaidaEstoque', on_delete=models.CASCADE)
    turma = models.OneToOneField('Turma', on_delete=models.CASCADE)
    alunos_presentes = models.ManyToManyField('Aluno')



A classe RetiradaMerenda está associada à ProgramacaoSaidaEstoque e registra informações sobre as retiradas realizadas por turmas específicas em relação a uma determinada programação de saída de estoque. Ela contém informações como a turma que realizou a retirada e a lista de alunos presentes na retirada.

Aqui está uma atualização na explicação do modelo de dados:

Programação de Saída de Estoque: Representa o planejamento e agendamento do envio de alimentos para a escola beneficiária. É uma relação de um para um com a escola beneficiária e está associada a uma ou mais movimentações de estoque.

Movimentação de Estoque: Representa a movimentação específica de saída de estoque relacionada à Programação de Saída de Estoque. Cada envio de alimentos para a escola resultará em uma ou mais movimentações de estoque correspondentes.

Retirada de Merenda: Representa as retiradas específicas de merenda relacionadas à Programação de Saída de Estoque. Cada retirada está associada a uma única turma e contém a lista de alunos presentes.

class ProgramacaoSaidaEstoque(models.Model):
    alimentos_a_enviar = models.ManyToManyField('Alimento')
    escola_beneficiaria = models.OneToOneField('Escola', on_delete=models.CASCADE)
    movimentacoes_estoque = models.ForeignKey('MovimentacaoEstoque', on_delete=models.CASCADE)

class MovimentacaoEstoque(models.Model):
    alimento = models.ForeignKey('Alimento', on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()

class RetiradaMerenda(models.Model):
    programacao_saida_estoque = models.ForeignKey('ProgramacaoSaidaEstoque', on_delete=models.CASCADE)
    turma = models.OneToOneField('Turma', on_delete=models.CASCADE)
    alunos_presentes = models.ManyToManyField('Aluno')





# Criando uma programação de saída de estoque
programacao = ProgramacaoSaidaEstoque.objects.create(
    escola_beneficiaria=escola_obj,
    movimentacoes_estoque=movimentacao_obj,
)

# Adicionando alimentos a serem enviados
programacao.alimentos_a_enviar.add(alimento1_obj, alimento2_obj)

# Criando uma movimentação de estoque relacionada à programação
movimentacao_estoque = MovimentacaoEstoque.objects.create(
    tipo='saida',
    alimento=alimento1_obj,
    quantidade=50,
    # Outros campos da movimentação de estoque
)

# Estabelecendo a relação entre a movimentação e a programação
programacao.movimentacoes_estoque = movimentacao_estoque
programacao.save()



"""
# RETIRADA DE MERENDA
# CONTROLE DE QUALIDADE
# OCORRÊNCIAS