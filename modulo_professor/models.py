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

        # Verifica se estamos atualizando o trimestre final para evitar recursão infinita
        if getattr(self, '_atualizando_trimestre_final', False):
            print("[INFO] Salvamento ignorado para evitar recursão no trimestre final.")
            super().save(*args, **kwargs)
            return

        print(f"[INFO] Salvando ComposicaoNotas para aluno={self.aluno}, grade={self.grade}, trimestre={self.trimestre}")

        # Calcula a nota com base nas regras definidas
        nota_calculada = self.calcular_nota_final()
        print(f"[DEBUG] Nota calculada: {nota_calculada}")

        if self.prova_paralela and self.prova_paralela > nota_calculada:
            self.nota_final = self.prova_paralela
            mensagem = "Nota da prova paralela foi maior e utilizada como nota final."
            self.anotacoes = f"{self.anotacoes}\n{mensagem}" if self.anotacoes else mensagem
            print(f"[INFO] Usando nota da prova paralela: {self.nota_final}")
        else:
            self.nota_final = nota_calculada
            print(f"[INFO] Usando nota calculada como nota final: {self.nota_final}")

        # Salva a nota atual
        super().save(*args, **kwargs)
        print(f"[SUCCESS] Nota salva para trimestre: {self.trimestre}")

        # Atualiza/insere em GestaoTurmas
        if self.aluno and self.grade and self.trimestre:
            gestao_turma, created = GestaoTurmas.objects.get_or_create(
                aluno=self.aluno,
                grade=self.grade,
                trimestre=self.trimestre,
                defaults={'notas': self.nota_final}
            )
            if created:
                print(f"[INFO] Criado novo registro em GestaoTurmas para {self.trimestre}")
            else:
                gestao_turma.notas = self.nota_final
                gestao_turma.save()
                print(f"[INFO] Atualizado registro em GestaoTurmas com nota: {self.nota_final}")

        # Atualiza a média no trimestre final
        try:
            tFinal = Trimestre.objects.get(final=True)
            print(f"[INFO] Trimestre final identificado: {tFinal}")

            media = ComposicaoNotas.objects.filter(
                aluno=self.aluno,
                grade=self.grade,
                nota_final__isnull=False
            ).exclude(trimestre=tFinal).aggregate(media=Avg('nota_final'))['media'] or Decimal('0.00')

            media_final = round(Decimal(media), 1)
            print(f"[INFO] Média calculada dos trimestres (exceto final): {media_final}")

            final_entry = ComposicaoNotas.objects.filter(
                aluno=self.aluno,
                grade=self.grade,
                trimestre=tFinal
            ).first()

            if final_entry:
                print(f"[INFO] Atualizando nota do trimestre final existente.")
                final_entry.nota_final = media_final
                final_entry._atualizando_trimestre_final = True
                final_entry.save(update_fields=['nota_final'])
            else:
                ComposicaoNotas.objects.create(
                    aluno=self.aluno,
                    grade=self.grade,
                    trimestre=tFinal,
                    nota_final=media_final
                )
                print(f"[SUCCESS] Criado novo registro no trimestre final com nota: {media_final}")

            # Atualiza a media_final em GestaoTurmas
            gestao_final, created = GestaoTurmas.objects.get_or_create(
                aluno=self.aluno,
                grade=self.grade,
                trimestre=tFinal,
                defaults={'media_final': media_final}
            )
            if not created:
                gestao_final.media_final = media_final
                gestao_final.save(update_fields=['media_final'])
                print(f"[INFO] Média final atualizada em GestaoTurmas: {media_final}")
            else:
                print(f"[INFO] Média final salva em novo GestaoTurmas para trimestre final: {media_final}")

        except Trimestre.DoesNotExist:
            print("[WARN] Nenhum trimestre com final=True foi encontrado.")




    def __str__(self):
        return  f"{self.aluno} - {self.trimestre} - {self.nota_final}"
    

    