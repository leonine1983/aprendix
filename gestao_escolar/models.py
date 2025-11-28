from django.db import models
from django.utils import timezone
from datetime import timedelta, date, datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_migrate, post_save, post_delete
from django.dispatch import receiver
from rh.models import Ano as AnoLetivo, Uf_Unidade_Federativa, Sexo, Bairro, Cidade, Encaminhamentos
from ckeditor_uploader.fields import RichTextUploadingField
from django.db import connection
from django.db.utils import OperationalError

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings



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
    nome = models.CharField(max_length=100)  
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
    LATERALIDADE_CHOICES = [
        ('destro', 'Destro'),
        ('canhoto', 'Canhoto'),
        ('ambidestro', 'Ambidestro'),
    ]

    nome_completo = models.CharField(
        max_length=120,
        null=False,
        default='Nome completo do aluno',
        verbose_name='Nome completo do aluno*'
    )
    nome_social = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default='',
        verbose_name='Nome social'
    )
    lateralidade = models.CharField(
        max_length=10,
        choices=LATERALIDADE_CHOICES,
        null=True,
        blank=True,
        verbose_name='Lateralidade (mão dominante)',
        help_text="Informe a mão dominante do aluno: "
                  "Destro (usa a mão direita), "
                  "Canhoto (usa a mão esquerda), "
                  "ou Ambidestro (usa ambas as mãos com igual habilidade)."
    )
    sexo = models.ForeignKey(Sexo, on_delete= models.CASCADE, verbose_name='Gênero sexual do aluno*', null=True)
    data_nascimento = models.DateField(verbose_name='Data de Nascimento*', null=True)    
    idade = models.IntegerField(null=True, blank=True)
    etnia = models.ForeignKey(Etnia, null=True, on_delete=models.CASCADE, verbose_name='Etnia do aluno*:')
    #aluno_inativo = models.BooleanField(default=False, null=True)
    tel_celular_aluno = models.CharField(max_length=30, null=False,  verbose_name='Nº de telefone do aluno*')    
    email = models.EmailField(max_length=200, null=False, verbose_name='Email*')
    # Endereço do aluno
    rua = models.CharField(max_length=100, null=False, default='Av., Rua, Travessa')
    #bairro = models.ForeignKey(Bairro, null=True, on_delete=models.CASCADE)    
    #cidade = models.ForeignKey(Cidade, null=True, on_delete=models.CASCADE)   
    #estado = models.ForeignKey(Uf_Unidade_Federativa, related_name="estado_relatec",verbose_name='Estado onde vive', null=True, on_delete=models.CASCADE)

    # Modificando os campos de endereço para usar CharField em vez de ForeignKey
    estado = models.CharField(max_length=10, null=True, blank=True, verbose_name='Estado onde vive')
    cidade = models.CharField(max_length=100, null=True, blank=True, verbose_name='Cidade onde vive')
    bairro = models.CharField(max_length=100, null=True, blank=True, verbose_name='Bairro onde vive')

    
    # Campos de naturalidade
    estado_naturalidade = models.CharField(max_length=10, null=True, verbose_name='Estado onde nasceu')
    cidade_naturalidade = models.CharField(max_length=100, null=True, verbose_name='Cidade onde nasceu')

    #naturalidade = models.ForeignKey(Cidade, null=True, on_delete=models.CASCADE, related_name="related_naturalidade", verbose_name='Cidade onde nasceu')
    #estado_naturalidade = models.ForeignKey(Uf_Unidade_Federativa, related_name="estado_nascimento",verbose_name='Estado onde nasceu', null=True, on_delete=models.CASCADE)
    nacionalidade = models.ForeignKey(Nacionalidade, on_delete=models.CASCADE, default=1, verbose_name='Nacionalidade*')



    # Informações Paternas e Maternas
    nome_mae = models.CharField(max_length=120, null=False, default='', verbose_name='Nome da Mãe*')
    CPF_mae = models.CharField(max_length=14, null=True, blank=True, default='000.000.000-00')   
    tel_celular_mae = models.CharField(max_length=30, null=True, verbose_name='Nº do celular do mãe*')
    nome_pai = models.CharField(max_length=120, null=True, default='Não consta')
    tel_celular_pai = models.CharField(max_length=30, null=True)          
    # Se exterior
    aluno_exterior = models.BooleanField(default=False, verbose_name="Marque se o aluno veio do Exterior")
    pais_origem = models.ForeignKey(Pais_origem, blank=True, null=True, on_delete=models.CASCADE)
    data_entrada_no_pais= models.DateField(null=True, blank=True)  
    documento_estrangeiro = models.CharField(max_length=30, null=True, blank=True)
    # condicoes fisicas e saude
    deficiencia_aluno = models.ForeignKey(Deficiencia_aluno, on_delete=models.CASCADE, null=True, verbose_name='Informe se o aluno possui deficiência*')        
    tipo_sanguineo = models.CharField(max_length=3, choices=choices, null=True, )    
    necessita_edu_especial = models.BooleanField(default=False,null=True, verbose_name='Selecione se o aluno precisa de algum atendimento especial')
    vacina_covid_19 = models.BooleanField(default=False, null=True,verbose_name='Selecione se o aluno tomou vacina contra a covid 19' )
    dose_vacina_covid_19 = models.IntegerField(null=True, blank=True, verbose_name='Preencha se o aluno tomou alguma dose da covid 19' )
    sindrome_de_Down = models.BooleanField(default=False,null=True, verbose_name='Selecione se o aluno for portador de Síndrome de Down')
    espectro_autista = models.BooleanField(default=False, null=True,verbose_name='Por favor, informe se o aluno possui Transtorno do Espectro Autista (TEA), para que possamos oferecer o apoio necessário') 
    
    beneficiario_aux_Brasil = models.BooleanField(default=False,null=True, verbose_name='Selecione se o aluno é beneficiário do Bolsa Família/Aux. Brasil')
    quilombola = models.BooleanField(default=False,null=True, verbose_name='Selecione se o aluno possui deficiência')
    irmao_gemeo = models.BooleanField(default=False, null=True, verbose_name='Selecione se o aluno possui irmão(s) gêmeos')   
    res_cadastro = models.CharField(max_length=120, null=True, default='Quem criou o cadastro')    
    res_atualiza_cadastro = models.CharField(max_length=120, null=True, default='Quem atualizou')       
    
    documento_espectro_autista = models.FileField(upload_to='documentos_aluno_TEA/', null=True, blank=True, verbose_name="Caso o aluno seja autista ou possua qualquer deficiência que requeira comprovação, faça o upload do laudo médico ou documentos pertinentes.")
    foto_aluno = models.ImageField(upload_to='imagem_aluno/', null=True, blank=True, verbose_name="Selecione uma imagem de perfil para o aluno.")

    # Documentação
    RG = models.CharField(max_length=14, null=True, blank=True, default='000.000.00-00')    
    RG_emissao = models.DateField(null=True, blank=True, default=timezone.now)  
    RG_UF = models.ForeignKey(Uf_Unidade_Federativa, on_delete=models.CASCADE, null=True, blank=True)
    orgao_emissor = models.CharField(max_length=5, null=True, blank=True)

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
    justificativa_falta_documento = models.CharField(max_length=2, choices=choice_justifica_falta_document, null=True, blank=True, verbose_name='Justificativa da falta de documentação')
    local_diferenciado = models.CharField(max_length=2, choices=choice_justifica_falta_document, null=True, blank=True, verbose_name='Local Diferenciado')
    obito = models.BooleanField(null=True, blank=True,default=False)
    data_obito = models.DateField(null=True, blank=True)

    # Controle de alteraçao
    criado_por = models.CharField(max_length=100, null=True, blank=True)
    data_create = models.DateField(null=True,  blank=True, auto_now_add=True)
    alterado_por = models.TextField(null=True, blank=True)
    data_alteracaoCadastro = models.DateTimeField(auto_now=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        print("principio")
        usuario = getattr(self, '_usuario_logado', None)

        if self.pk and usuario:
            data_atual = timezone.now().strftime("%d/%m/%Y %H:%M")
            novo_registro = f"{usuario} - {data_atual}"
            if self.alterado_por:
                self.alterado_por += f"\n{novo_registro}"
                print("esta aqui se alterado")
            else:
                self.alterado_por = novo_registro
                print("esta aqui se não alterado")

        # 🔸 Chame SEMPRE o save real
        super().save(*args, **kwargs)




    """
     def save(self, *args, **kwargs):
        # Captura o usuário, se for passado pelo contexto
        usuario = getattr(self, '_usuario_logado', None)

        # Registra log apenas se for uma atualização e houver usuário
        if self.pk and usuario:
            data_atual = timezone.now().strftime("%d/%m/%Y %H:%M")
            novo_registro = f"{usuario} - {data_atual}"
            if self.alterado_por:
                self.alterado_por += f"\n{novo_registro}"
            else:
                self.alterado_por = novo_registro

        super().save(*args, **kwargs)
    
    """




    def e_aniversario_hoje(self):
        hoje = datetime.now().date()
        return (self.data_nascimento and 
                self.data_nascimento.month == hoje.month and 
                self.data_nascimento.day == hoje.day)

    def __str__(self):
        return self.nome_completo 
    
class AlunoUser(models.Model):
    aluno = models.OneToOneField(Alunos, null=True, on_delete=models.CASCADE, related_name='alunoUser_related',  verbose_name='Aluno Usuario*:')
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE,related_name='userAluno_related', verbose_name='usuario aluno*:')

    class Meta:
        ordering = ['aluno']

    def __str__(self):
        return f'{self.aluno.nome_completo} - Login: {self.aluno.login_aluno} - Senha: {self.aluno.senha}'



class Disciplina(models.Model):
    CAMPO_CONHECIMENTO_CHOICES = [
        ('linguagens', 'Linguagens'),
        ('matematica', 'Matemática'),
        ('ciencias_natureza', 'Ciências da Natureza'),
        ('ciencias_humanas', 'Ciências Humanas'),
        ('outras', 'Outras'),
    ]

    nome = models.CharField(max_length=100)
    ordem_historico = models.FloatField(null=True)
    n_A = models.BooleanField(verbose_name="Destacar como N/S (Não avaliado) nos impressos", default=False, null=True)
    faltas = models.BooleanField(verbose_name="Não permitir lançamento de faltas", default=False, null=True)
    notas = models.BooleanField(verbose_name="Não permitir lançamento de notas", default=False, null=True)
    historico_escolar = models.BooleanField(verbose_name="Não mostrar no histórico escolar", default=False, null=True)
    papeletas = models.BooleanField(verbose_name="Não mostrar em papeletas", default=False, null=True)
    ata_final = models.BooleanField(verbose_name="Não mostrar em Atas Finais", default=False, null=True)
    

    campo_conhecimento = models.CharField(
        max_length=30,
        choices=CAMPO_CONHECIMENTO_CHOICES,
        verbose_name='Campo do Conhecimento',
        default='matematica',
        help_text='Selecione o campo do conhecimento da disciplina'
    )

    class Meta:
        ordering = ['ordem_historico']

    def __str__(self):
        return self.nome


class Compatibilidade_EducaCenso(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class GrauEscolar(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Grau/Nível Escolar")

    def __str__(self):
        return self.nome


class Serie_Escolar(models.Model):
    nome = models.CharField(max_length=30)
    nivel_escolar = models.ForeignKey(GrauEscolar, null=False, on_delete=models.CASCADE)
    compatibilidade_EducaCenso = models.ForeignKey(Compatibilidade_EducaCenso, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome 

turno = {
    ('Matutino', 'Matutino'),
    ('Verspertino', 'Verspertino'),
    ('Noturno', 'Noturno')
}

# Modelos para a MATRÍCULA PÚBLICA ----------------------------------------------------------------

class EscolaMatriculaOnline(models.Model):
    escola = models.ForeignKey('rh.Escola', related_name="escolaOnline",  on_delete=models.CASCADE)
    ano_letivo = models.ForeignKey(AnoLetivo, on_delete=models.CASCADE)
    data_inicio = models.DateField(null=True)
    data_fim = models.DateField(null=True)   
    ativo =models.BooleanField(default=False)

    class Meta:
        ordering = ['-data_inicio']

    def __str__(self):
        return f'{self.escola} - {self.ano_letivo.ano}'


class SerieOnline(models.Model):
    escola = models.ForeignKey(EscolaMatriculaOnline, related_name='escolaOnlineRelated', on_delete=models.CASCADE)    
    serie =  models.ForeignKey(Serie_Escolar, related_name='seriesOnlineRelated', on_delete=models.CASCADE)
    turno = models.CharField(choices=turno, null=False, default=1, max_length=12)                
    quantidade_vagas = models.IntegerField(default=36) 
    vagas_disponiveis = models.IntegerField(null=True)    

    class Meta:
        ordering = ['serie']
    
    def __str__(self):
        return f'{self.serie.nome} - {self.escola.ano_letivo.ano}'
    

class MatriculasOnline(models.Model):    
    aluno = models.ForeignKey(Alunos, related_name='related_matriculaOnline_alunos', on_delete=models.CASCADE)
    serie = models.ForeignKey(SerieOnline, related_name="related_serie_matricula", on_delete=models.CASCADE)
    pendecia = RichTextUploadingField(null=True, blank=True)  
    impugnar = models.BooleanField(default=False)
    confirma = models.BooleanField(default=False)
    data_matricula = models.DateField( auto_now=True) 

    def __str__(self):
        return self.aluno.nome_completo
    
# Defina os sinais fora da classe
@receiver(post_save, sender=MatriculasOnline)
@receiver(post_delete, sender=MatriculasOnline)
def atualizar_vagas_disponiveis(sender, instance, **kwargs):
    # Obtenha a série associada
    serie_online = instance.serie

    # Conte o número de matrículas para esta série
    total_matriculas = MatriculasOnline.objects.filter(serie=serie_online).count()

    # Atualize o campo vagas_disponiveis
    serie_online.vagas_disponiveis = serie_online.quantidade_vagas - total_matriculas
    serie_online.save()

# FIM Modelos para a MATRÍCULA PÚBLICA ----------------------------------------------------------------


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

    class Meta:
        ordering = ['nome']

  
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
    # limite_faltas = models.IntegerField(null=True)

    

    def __str__(self):
        return f'{self.disciplina.nome} - {self.professor.encaminhamento}'   


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
    cod_matricula = models.TextField(max_length=200, null=True, default='2025-001')
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
    aprovado = models.BooleanField(default=False)
    aprovado_conselho = models.BooleanField(default=False)
    aprovado_recupera = models.BooleanField(default=False)
    reprovado_recupera = models.BooleanField(default=False)
    reprovado_conselho = models.BooleanField(default=False)
    foi_a_recupera = models.BooleanField(default=False)
    

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

            trimestre = Trimestre.objects.all()
            for tri in trimestre:
                ParecerDescritivo.objects.create(
                    matricula = Matriculas.objects.get(id=instance.id),
                    trimestre = Trimestre.objects.get(id = tri.id)
                )

    class Meta:
        ordering = ['aluno']

    def __str__(self):
        return self.aluno.nome_completo
    
  
class TiposRemanejamentos(models.Model):
    nome = models.CharField(max_length=26, null=True, verbose_name="Tipo de remanejamento")
    description = models.TextField(max_length=500, verbose_name="Descreve o tipo de remanejamento")

    def __str__(self):
        return self.nome  
    

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
    
    
# Modelos relacionados ao horário de aula e presença dos alunos
class Validade_horario(models.Model):    
    escola = models.ForeignKey('rh.Escola', related_name='escola_validade_related', on_delete=models.CASCADE, null=True)
    turma = models.ForeignKey(Turmas,null=True, related_name='turma_Validade_related', on_delete=models.CASCADE)  
    nome_validade = models.CharField(max_length=30)
    data_inicio = models.DateField(null=True)
    data_fim = models.DateField(null=True)     
    horario_ativo = models.BooleanField(default=False)

    def __str__(self):
        return (f'{self.nome_validade}: {self.data_inicio} a {self.data_fim}')   
    

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
    
"""
class Presenca(models.Model):
    horario = models.ForeignKey(Horario, related_name='presencas', on_delete=models.CASCADE)
    matricula = models.ForeignKey(Matriculas, related_name='presencas_aluno', on_delete=models.CASCADE)
    presente = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.matricula.aluno.nome_completo} - {self.horario} - {"Presente" if self.presente else "Ausente"}'
"""

class Presenca(models.Model):
    matricula = models.ForeignKey(Matriculas, related_name='presencas_aluno', on_delete=models.CASCADE)
    data = models.DateField(
        verbose_name="Data da Aula",
        help_text="Informe a data em que a aula foi ministrada."
    )

    trimestre = models.ForeignKey(
        Trimestre, 
        related_name='presencas_alunoTrimestre', 
        on_delete=models.CASCADE,
        verbose_name="Trimestre atual",
        help_text="Informe o trimestre em que a presença do aluno está sendo registrada.",
        null=True)
    
    controle_diario = models.BooleanField(default=True)

    turma_disciplina = models.ForeignKey(
        TurmaDisciplina,
        related_name='presencas_por_disciplina',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    aula_numero = models.PositiveSmallIntegerField(null=True, blank=True)

    presente = models.BooleanField(default=True)
    observacao = models.TextField(null=True, blank=True)

    # ✅ Horário como referência 
    horario = models.ForeignKey(
        Horario,
        related_name='presencas',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        #app_label = 'modulo_professor' 
        verbose_name = 'Frequência do aluno'
        verbose_name_plural = 'Frequências dos alunos'
        unique_together = ('matricula', 'data', 'turma_disciplina', 'aula_numero')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.atualizar_faltas_gestao_turmas()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.atualizar_faltas_gestao_turmas()

    def atualizar_faltas_gestao_turmas(self):
        if not self.trimestre or not self.turma_disciplina:
            print("⚠️ Trimestre ou disciplina não definidos. Faltas não foram atualizadas.")
            return

        # Filtrar todas as presenças do aluno naquela disciplina e trimestre
        faltas = Presenca.objects.filter(
            matricula=self.matricula,
            turma_disciplina=self.turma_disciplina,
            trimestre=self.trimestre,
            presente=False
        )

        total_faltas = faltas.count()

        try:
            gestao = GestaoTurmas.objects.get(
                aluno=self.matricula,
                grade=self.turma_disciplina,
                trimestre=self.trimestre
            )
            gestao.faltas = total_faltas
            gestao.faltas_total = total_faltas
            gestao.save()
            print(f"✅ Faltas atualizadas para {gestao.aluno.aluno.nome_completo}: {total_faltas} faltas registradas.")
        except GestaoTurmas.DoesNotExist:
            print(f"⚠️ GestaoTurmas não encontrada para {self.matricula}. Nenhuma atualização feita.")


    def __str__(self):
        nome = self.matricula.aluno.nome_completo
        tipo = "Dia" if self.controle_diario else f"Aula {self.aula_numero} - {self.turma_disciplina}"
        status = "Presente" if self.presente else "Ausente"
        return f'{nome} - {self.data} - {tipo} - {status}'


class GestaoTurmas(models.Model):
    aluno = models.ForeignKey(Matriculas, related_name='gestao_turmas_related', null=True, on_delete=models.CASCADE)
    grade = models.ForeignKey(TurmaDisciplina, null=True, related_name='grade_disciplina', on_delete=models.CASCADE)
    trimestre = models.ForeignKey(Trimestre, related_name='trimestre_related_turma', null=True, on_delete=models.CASCADE)
    notas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    faltas = models.IntegerField(null=True, blank=True)
    profissional_resp = models.CharField(max_length=40, null=True)
    data_hora_mod = models.DateTimeField(null=True)

    parecer_descritivo = models.TextField(max_length=500, default="Ainda não há parecer do aluno para esse período")

    faltas_total = models.IntegerField(null=True, blank=True)
    recuperacao_final = models.DecimalField("Recuperaçao Final", max_digits=5, decimal_places=2, null=True, blank=True)
    media_final = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)   

    media_anterior_conselho_classe = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    conselho_classe = models.BooleanField(default=False)

    aprovado = models.BooleanField(default=False)
    reprovado_faltas = models.BooleanField(default=False)
    reprovado_faltas_disciplina = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.aluno.aluno.nome_completo
    

    def save(self, *args, **kwargs):
        from django.db.models import Avg, Sum
        from modulo_professor.models import ComposicaoNotas
        from gestao_escolar.models import GestaoTurmas, Trimestre

        # Evita loop infinito
        if getattr(self, '_atualizando_por_composicao', False):
            super().save(*args, **kwargs)
            return

        super().save(*args, **kwargs)

        # 🔹 Atualiza ou cria registro em ComposicaoNotas
        if self.notas is not None:
            comp_nota, created = ComposicaoNotas.objects.get_or_create(
                aluno=self.aluno,
                grade=self.grade,
                trimestre=self.trimestre,
                defaults={'nota_final': self.notas}
            )
            mensagem = f"Nota atualizada por {self.profissional_resp}"
            if not created:
                comp_nota.nota_final = self.notas
                comp_nota.anotacoes = f"{comp_nota.anotacoes}\n{mensagem}" if comp_nota.anotacoes else mensagem
            else:
                comp_nota.anotacoes = mensagem
            comp_nota._atualizando_por_gestao = True
            comp_nota.save()

        # 🔹 Calcula média dos trimestres não finais
        media = GestaoTurmas.objects.filter(
            aluno=self.aluno,
            grade=self.grade,
            trimestre__final=False,
            notas__isnull=False
        ).aggregate(media=Avg('notas'))['media'] or 0

        # 🔹 Calcula total de faltas em todos os trimestres
        total_faltas = GestaoTurmas.objects.filter(
            aluno=self.aluno,
            grade=self.grade
        ).aggregate(total=Sum('faltas'))['total'] or 0

        # 🔹 Atualiza média e total de faltas em todos os registros do aluno/grade
        GestaoTurmas.objects.filter(
            aluno=self.aluno,
            grade=self.grade
        ).update(media_final=media, faltas_total=total_faltas)

        # 🔹 Reprovação automática por faltas
        # 🔹 Reprovação automática por faltas
        if self.grade and self.grade.carga_horaria_anual:
            limite_faltas = self.grade.carga_horaria_anual * 0.25  # 25% do total
            reprovado = total_faltas >= limite_faltas

            from django.db.models import Sum

            # 🔸 Atualiza lista de disciplinas reprovadas por faltas (todas da turma)
            disciplinas_reprovadas = (
                GestaoTurmas.objects
                .filter(
                    aluno=self.aluno,
                    grade__turma=self.grade.turma,
                )
                .values('grade__disciplina__nome', 'grade__carga_horaria_anual')
                .annotate(total_faltas=Sum('faltas'))
            )

            disciplinas_reprovadas_nomes = []
            for d in disciplinas_reprovadas:
                limite = d['grade__carga_horaria_anual'] * 0.25 if d['grade__carga_horaria_anual'] else 0
                if d['total_faltas'] and d['total_faltas'] >= limite:
                    disciplinas_reprovadas_nomes.append(d['grade__disciplina__nome'])

            disciplinas_texto = ', '.join(sorted(set(disciplinas_reprovadas_nomes))) if disciplinas_reprovadas_nomes else None

            # 🔹 Atualiza o campo reprovado_faltas em todos os trimestres da turma do aluno
            GestaoTurmas.objects.filter(
                aluno=self.aluno,
                grade__turma=self.grade.turma
            ).update(reprovado_faltas=reprovado)

            # 🔹 Se total_faltas for menor que o limite, limpa ou atualiza as disciplinas reprovadas
            if not reprovado:
                # Se ainda existirem outras disciplinas acima do limite, mantém apenas elas
                GestaoTurmas.objects.filter(
                    aluno=self.aluno,
                    grade__turma=self.grade.turma
                ).update(
                    reprovado_faltas=False,
                    reprovado_faltas_disciplina=disciplinas_texto
                )
            else:
                # Caso contrário, marca reprovação e atualiza lista de disciplinas
                GestaoTurmas.objects.filter(
                    aluno=self.aluno,
                    grade__turma=self.grade.turma
                ).update(
                    reprovado_faltas=True,
                    reprovado_faltas_disciplina=disciplinas_texto
                )

                
    
class ParecerDescritivo(models.Model):
    matricula = models.ForeignKey(Matriculas, blank=True, on_delete=models.CASCADE, related_name='pareceres_aluno')
    trimestre = models.ForeignKey(Trimestre, related_name='trimestre_related_turma_parecer', null=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')    
    author_created = models.CharField(max_length=50,  null=True, blank=True, verbose_name='Autor da criação')
    atualizado_em = models.DateTimeField(auto_now=True,  verbose_name='Data da Última Atualização')
    author_atualiza = models.CharField(max_length=50, null=True, blank=True, verbose_name='Autor da atualização')

    # Aspectos da BNCC para Creche e Anos Iniciais
    aspectos_cognitivos =  RichTextUploadingField(null=True, blank=True)       
    aspectos_socioemocionais =  RichTextUploadingField(null=True, blank=True)  
    aspectos_fisicos_motoras =  RichTextUploadingField(null=True, blank=True)  
    habilidades =  RichTextUploadingField(null=True, blank=True)               
    conteudos_abordados =  RichTextUploadingField(null=True, blank=True)       
    interacao_social =  RichTextUploadingField(null=True, blank=True)          
    comunicacao =  RichTextUploadingField(null=True, blank=True)               
    consideracoes_finais =  RichTextUploadingField(null=True, blank=True)      
    observacao_coordenador =  RichTextUploadingField(null=True, blank=True)  
    resumo = RichTextUploadingField(null=True, blank=True) 

    def __str__(self):
        return f'Parecer de {self.matricula.aluno} - Matriculado em {self.matricula.data_matricula}'
    

# Disponibilização do CAAE -------------------------------------------------------------------------------------------------------------------------
class AtendimentoEspecializado(models.Model):
    nome = models.CharField(max_length=30, null=False)
    descricao = models.TextField(max_length=500)

    def __str__(self):
        return self.nome

"""
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
"""

class DiaSemana(models.Model):
    nome_dia = models.CharField(max_length=10)
    numero_dia = models.IntegerField()
    
    class Meta:
        ordering = ['numero_dia']

    def __str__(self):
        return self.nome_dia

# signals.py (ou no final do models.py, mas recomendo signals.py)
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TurmaDisciplina, GestaoTurmas, Matriculas, Trimestre

@receiver(post_save, sender=TurmaDisciplina)
def cria_registros_gestao_turmas(sender, instance, created, **kwargs):
    if created:  # Só quando criar a TurmaDisciplina
        alunos = Matriculas.objects.filter(turma=instance.turma)
        trimestres = Trimestre.objects.filter(final=False)

        for matricula in alunos:
            for trimestre in trimestres:
                if not GestaoTurmas.objects.filter(
                    aluno=matricula,
                    grade=instance,
                    trimestre=trimestre
                ).exists():
                    GestaoTurmas.objects.create(
                        aluno=matricula,
                        grade=instance,
                        trimestre=trimestre,
                        notas=0,
                        faltas=0
                    )


# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Matriculas, TurmaDisciplina, GestaoTurmas, Trimestre

@receiver(post_save, sender=Matriculas)
def cria_registros_para_matricula(sender, instance, created, **kwargs):
    """
    Quando cria uma nova matrícula, gera registros em GestaoTurmas
    para todas as disciplinas já existentes na turma e trimestres ativos.
    """
    if created:
        # Todas as disciplinas da turma do aluno
        grades = TurmaDisciplina.objects.filter(turma=instance.turma)
        # Trimestres que ainda não são finais
        trimestres = Trimestre.objects.filter(final=False)

        for grade in grades:
            for trimestre in trimestres:
                exists = GestaoTurmas.objects.filter(
                    aluno=instance,
                    grade=grade,
                    trimestre=trimestre
                ).exists()

                if not exists:
                    GestaoTurmas.objects.create(
                        aluno=instance,
                        grade=grade,
                        trimestre=trimestre,
                        notas=0,
                        faltas=0
                    )

