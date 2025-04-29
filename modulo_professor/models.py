from django.db import models
from gestao_escolar.models import Matriculas, TurmaDisciplina, Trimestre, GestaoTurmas
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
    nota_final = models.DecimalField("Nota Final", max_digits=5, decimal_places=2, null=True, blank=True)

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
        from decimal import Decimal

        # Calcula e atualiza a nota final
        self.nota_final = self.calcular_nota_final()
        super().save(*args, **kwargs)

        # Atualiza ou cria o registro correspondente em GestaoTurmas
        if self.aluno and self.grade and self.trimestre:
            gestao_turma, created = GestaoTurmas.objects.get_or_create(
                aluno=self.aluno,
                grade=self.grade,
                trimestre=self.trimestre,
                defaults={'notas': self.nota_final}
            )
            if not created:
                gestao_turma.notas = self.nota_final
                gestao_turma.save()


    def __str__(self):
        return self.aluno.aluno.nome_completo
    

    