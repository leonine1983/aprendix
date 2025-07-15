from django.db import models
from gestao_escolar.models import Matriculas, TurmaDisciplina, Trimestre, GestaoTurmas, Horario
from decimal import Decimal



class ComposicaoNotas(models.Model):
    """
    Model que representa a composição das notas de um aluno em uma disciplina
    durante um determinado trimestre. Armazena os componentes individuais da nota
    (prova, trabalho, participação e tarefas), calcula automaticamente a nota final
    com base nos pesos definidos, e permite o registro de anotações adicionais.

    Campos:
        - aluno: referência à matrícula do aluno.
        - grade: referência à disciplina da turma.
        - trimestre: trimestre letivo correspondente.
        - prova: nota da prova (peso 50%).
        - trabalho: nota do trabalho (peso 20%).
        - participacao: nota de participação (peso 15%).
        - tarefas: nota de tarefas (peso 15%).
        - nota_final: nota total calculada automaticamente.
        - anotacoes: campo livre para observações sobre o aluno.
    """
    aluno = models.ForeignKey(
        Matriculas,
        related_name='compoeNotaAlunos_related',
        null=True,
        on_delete=models.CASCADE
    )
    grade = models.ForeignKey(
        TurmaDisciplina,
        null=True,
        related_name='compoeNota_disciplina',
        on_delete=models.CASCADE
    )
    trimestre = models.ForeignKey(
        Trimestre,
        related_name='compoeNotatrimestre_related',
        null=True,
        on_delete=models.CASCADE
    )

    prova = models.DecimalField("Prova (50%)", max_digits=5, decimal_places=2, null=True, blank=True)
    trabalho = models.DecimalField("Trabalho (20%)", max_digits=5, decimal_places=2, null=True, blank=True)
    participacao = models.DecimalField("Participação (15%)", max_digits=5, decimal_places=2, null=True, blank=True)
    tarefas = models.DecimalField("Tarefas (15%)", max_digits=5, decimal_places=2, null=True, blank=True)
    prova_paralela = models.DecimalField("Prova Paralela)", max_digits=5, decimal_places=2, null=True, blank=True)
    nota_final = models.DecimalField("Nota Final", max_digits=5, decimal_places=2, null=True, blank=True)
    media_final = models.DecimalField("Media Final", max_digits=5, decimal_places=2, null=True, blank=True)
    recuperacao_final = models.DecimalField("Recuperaçao Final", max_digits=5, decimal_places=2, null=True, blank=True)

    anotacoes = models.TextField("Anotações", null=True, blank=True)

    from decimal import Decimal

    def calcular_nota_final(self):
        """Calcula a nota final com base nos pesos definidos.
        Campos None são tratados como zero."""
        
        prova = self.prova or Decimal('0')
        trabalho = self.trabalho or Decimal('0')
        participacao = self.participacao or Decimal('0')
        tarefas = self.tarefas or Decimal('0')

        return round(
            prova * Decimal('0.5') +
            trabalho * Decimal('0.2') +
            participacao * Decimal('0.15') +
            tarefas * Decimal('0.15'),
            2
        )

    def save(self, *args, **kwargs):
        from django.db.models import Avg
        from decimal import Decimal

        # 🔁 FLAG: Verifica se o salvamento está sendo feito pela Gestão de Turmas.
        # Se estiver, evita atualizar GestaoTurmas novamente e interrompe aqui.
        if getattr(self, '_atualizando_por_gestao', False):
            super().save(*args, **kwargs)
            return

        print(f"[INFO] Salvando ComposicaoNotas para aluno={self.aluno}, grade={self.grade}, trimestre={self.trimestre}")

        nota_calculada = self.calcular_nota_final()
        print(f"[DEBUG] Nota calculada: {nota_calculada}")

        if self.prova_paralela and self.prova_paralela > nota_calculada:
            self.nota_final = self.prova_paralela
            mensagem = "Nota da prova paralela foi maior e utilizada como nota final."
            self.anotacoes = f"{self.anotacoes}\n{mensagem}" if self.anotacoes else mensagem
        else:
            self.nota_final = nota_calculada

        super().save(*args, **kwargs)

        # Atualiza ou cria em GestaoTurmas, a menos que estejamos no trimestre final
        if self.aluno and self.grade and self.trimestre:
            gestao_turma, created = GestaoTurmas.objects.get_or_create(
                aluno=self.aluno,
                grade=self.grade,
                trimestre=self.trimestre,
                defaults={'notas': self.nota_final}
            )
            if not created:
                # 🔁 FLAG: Evita recursão marcando que a atualização veio de ComposicaoNotas
                gestao_turma._atualizando_por_composicao = True
                gestao_turma.notas = self.nota_final
                gestao_turma.save()

    def __str__(self):
        return  f"{self.aluno} - {self.trimestre} - {self.nota_final}"
    
    
from django.db import models
from django.core.exceptions import ValidationError
from ckeditor_uploader.fields import RichTextUploadingField
from gestao_escolar.models import TurmaDisciplina

class PlanoDeAula(models.Model):
    turma_disciplina = models.ForeignKey(
        TurmaDisciplina,
        on_delete=models.CASCADE,
        related_name='planos_de_aula',
        verbose_name="Turma / Disciplina"
    )

    tema = models.CharField(
        max_length=150,
        verbose_name="Tema ou assunto abordado no plano de aula",
        help_text="Descreva brevemente o conteúdo principal ou tema do plano de aula.",
        default="Tema não especificado"
    )

    data_inicio = models.DateField(
        verbose_name="Data de Início",
        help_text="Data inicial do período do plano de aula"
    )
    data_fim = models.DateField(
        verbose_name="Data de Fim",
        help_text="Data final do período do plano de aula"
    )

    conteudo_planejado = RichTextUploadingField(
        verbose_name="Conteúdo Planejado"
    )
    objetivo_geral = RichTextUploadingField(
        verbose_name="Objetivo Geral"
    )
    competencias_bncc = RichTextUploadingField(
        verbose_name="Competências da BNCC",
        help_text="Informe os códigos e descrições das competências segundo a BNCC"
    )
    habilidades_bncc = RichTextUploadingField(
        verbose_name="Habilidades da BNCC",
        help_text="Informe os códigos e descrições das habilidades segundo a BNCC"
    )
    metodologia = RichTextUploadingField(
        verbose_name="Metodologia",
        blank=True, null=True
    )
    recursos_didaticos = RichTextUploadingField(
        verbose_name="Recursos Didáticos",
        blank=True, null=True
    )

    class Meta:
        verbose_name = "Plano de Aula"
        verbose_name_plural = "Planos de Aula"
        ordering = ['-data_inicio']

    def __str__(self):
        return f'{self.tema} - {self.data_inicio.strftime("%d/%m/%Y")} a {self.data_fim.strftime("%d/%m/%Y")}'

    def clean(self):
        super().clean()
        if self.data_fim < self.data_inicio:
            raise ValidationError({
                'data_fim': "A data final não pode ser anterior à data inicial."
            })



class AulaDada(models.Model):
    plano = models.ForeignKey(
        PlanoDeAula,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='aulas_relacionadas',
        verbose_name="Plano de Aula",
        help_text="Associe um plano de aula previamente elaborado, se houver."
    )

    turma_disciplina = models.ForeignKey(
        TurmaDisciplina,
        on_delete=models.CASCADE,
        related_name='aulas_dadas',
        verbose_name="Disciplina",
        help_text="Selecione a combinação de turma e disciplina a que esta aula pertence."
        )

    data = models.DateField(
        verbose_name="Data da Aula",
        help_text="Informe a data em que a aula foi ministrada."
    )

    hora_inicio = models.TimeField(
        verbose_name="Horário de Início",
        help_text="Informe o horário de início da aula."
    )

    aula_numero = models.PositiveSmallIntegerField(
        blank=True,
        default=1,
        verbose_name="Número da Aula",
        help_text="Informe se esta é a 1ª, 2ª ou 3ª aula do dia."
    )

    hora_fim = models.TimeField()
    
    conteudo_dado = RichTextUploadingField(
        verbose_name="Conteúdo Ministrado",
        help_text="Descreva de forma objetiva o conteúdo efetivamente trabalhado em sala de aula."
    )

    observacoes = RichTextUploadingField(
        verbose_name="Observações Gerais",
        help_text="Registre informações adicionais relevantes sobre a aula, como participação dos alunos, imprevistos ou outros comentários.",
        blank=True,
        null=True
    )



    def __str__(self):
        return f'{self.turma_disciplina} - {self.data}'
    

class AnexoAula(models.Model):
    aula = models.ForeignKey(
        AulaDada,
        on_delete=models.CASCADE,
        related_name='anexos'
    )
    arquivo = models.FileField(upload_to='anexos_aulas/')
    descricao  = RichTextUploadingField(
        verbose_name="Observações",
        blank=True,
        null=True
    )

    def __str__(self):
        return f'Anexo para aula {self.aula.id}'
