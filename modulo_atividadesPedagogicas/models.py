from django.db import models
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField


# =====================================================
# MODO STANDALONE (DESCOMENTAR EM OUTROS PROJETOS)
# =====================================================

# class NivelEnsino(models.Model):
#
#     nome = models.CharField(
#         max_length=100,
#         unique=True
#     )
#
#     descricao = models.TextField(
#         blank=True
#     )
#
#     ordem = models.PositiveIntegerField(
#         default=0
#     )
#
#     class Meta:
#         ordering = ["ordem", "nome"]
#
#     def __str__(self):
#         return self.nome
#
#
# class SerieEscolar(models.Model):
#
#     nivel = models.ForeignKey(
#         NivelEnsino,
#         on_delete=models.CASCADE,
#         related_name="series"
#     )
#
#     nome = models.CharField(
#         max_length=100
#     )
#
#     ordem = models.PositiveIntegerField(
#         default=0
#     )
#
#     class Meta:
#         ordering = ["ordem"]
#
#     def __str__(self):
#         return self.nome
#
#
# class Disciplina(models.Model):
#
#     nome = models.CharField(
#         max_length=100,
#         unique=True
#     )
#
#     class Meta:
#         ordering = ["nome"]
#
#     def __str__(self):
#         return self.nome


# =====================================================
# MODO GESTÃO ESCOLAR
# =====================================================

from gestao_escolar.models import (
    Disciplina,
    GrauEscolar,
    Serie_Escolar
)


# =====================================================
# BNCC
# =====================================================

class HabilidadeBNCC(models.Model):

    codigo = models.CharField(
        max_length=20,
        unique=True
    )

    eixo = models.CharField(
        max_length=100,
        blank=True
    )

    unidade_tematica = models.CharField(
        max_length=150,
        blank=True
    )

    ano_inicio = models.PositiveSmallIntegerField(
        null=True,
        blank=True
    )

    ano_fim = models.PositiveSmallIntegerField(
        null=True,
        blank=True
    )

    descricao = models.TextField()

    def __str__(self):
        return self.codigo

# =====================================================
# TAGS
# =====================================================

class Tag(models.Model):

    nome = models.CharField(
        max_length=50,
        unique=True
    )

    cor = models.CharField(
        max_length=20,
        default="#0d6efd"
    )

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


# =====================================================
# CATEGORIAS
# =====================================================

class CategoriaJogo(models.Model):

    nome = models.CharField(
        max_length=100,
        unique=True
    )

    descricao = models.TextField(
        blank=True
    )

    class Meta:
        ordering = ["nome"]
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.nome


# =====================================================
# JOGO PEDAGÓGICO
# =====================================================

class JogoPedagogico(models.Model):

    class Modalidade(models.TextChoices):
        PLUGADO = "plugado", "Plugado"
        DESPLUGADO = "desplugado", "Desplugado"
        HIBRIDO = "hibrido", "Híbrido"

    class Dificuldade(models.TextChoices):
        FACIL = "facil", "Fácil"
        MEDIO = "medio", "Médio"
        AVANCADO = "avancado", "Avançado"

    titulo = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    resumo = models.TextField()

    descricao = RichTextUploadingField()

    objetivo_pedagogico = RichTextUploadingField()

    imagem_capa = models.ImageField(
        upload_to="jogos/capas/",
        blank=True,
        null=True
    )

    icone = models.CharField(
        max_length=50,
        blank=True
    )

    link_externo = models.URLField(
        blank=True
    )

    modalidade = models.CharField(
        max_length=20,
        choices=Modalidade.choices,
        default=Modalidade.PLUGADO
    )

    dificuldade = models.CharField(
        max_length=20,
        choices=Dificuldade.choices,
        default=Dificuldade.FACIL
    )

    tempo_estimado = models.PositiveIntegerField(
        default=30,
        help_text="Tempo em minutos"
    )

    quantidade_jogadores = models.CharField(
        max_length=100,
        blank=True
    )

    destaque = models.BooleanField(
        default=False
    )

    publicado = models.BooleanField(
        default=True
    )

    visualizacoes = models.PositiveIntegerField(
        default=0
    )

    # =====================================
    # RELACIONAMENTOS COM GESTÃO ESCOLAR
    # =====================================

    graus_escolares = models.ManyToManyField(
        GrauEscolar,
        related_name="jogos_pedagogicos",
        blank=True
    )

    series = models.ManyToManyField(
        Serie_Escolar,
        related_name="jogos_pedagogicos",
        blank=True
    )

    disciplinas = models.ManyToManyField(
        Disciplina,
        related_name="jogos_pedagogicos",
        blank=True
    )

    habilidades_bncc = models.ManyToManyField(
        HabilidadeBNCC,
        blank=True
    )

    categorias = models.ManyToManyField(
        CategoriaJogo,
        blank=True
    )

    tags = models.ManyToManyField(
        Tag,
        blank=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["titulo"]
        verbose_name = "Jogo Pedagógico"
        verbose_name_plural = "Jogos Pedagógicos"

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.titulo)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo


# =====================================================
# ETAPAS DO JOGO
# =====================================================

class EtapaJogo(models.Model):

    jogo = models.ForeignKey(
        JogoPedagogico,
        on_delete=models.CASCADE,
        related_name="etapas"
    )

    titulo = models.CharField(
        max_length=200
    )

    descricao = RichTextUploadingField()

    ordem = models.PositiveIntegerField(
        default=1
    )

    class Meta:
        ordering = ["ordem"]

    def __str__(self):
        return self.titulo


# =====================================================
# APLICAÇÃO PEDAGÓGICA
# =====================================================

class AplicacaoPedagogica(models.Model):

    jogo = models.OneToOneField(
        JogoPedagogico,
        on_delete=models.CASCADE,
        related_name="aplicacao"
    )

    organizacao_turma = RichTextUploadingField(
        blank=True,
        null=True
    )

    materiais_necessarios = RichTextUploadingField(
        blank=True,
        null=True
    )

    metodologia = RichTextUploadingField(
        blank=True,
        null=True
    )

    adaptacoes = RichTextUploadingField(
        blank=True,
        null=True
    )

    avaliacao = RichTextUploadingField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.jogo.titulo


# =====================================================
# ARQUIVOS
# =====================================================

class ArquivoJogo(models.Model):

    jogo = models.ForeignKey(
        JogoPedagogico,
        on_delete=models.CASCADE,
        related_name="arquivos"
    )

    titulo = models.CharField(
        max_length=200
    )

    arquivo = models.FileField(
        upload_to="jogos/arquivos/"
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.titulo


# =====================================================
# GALERIA DE IMAGENS
# =====================================================

class ImagemJogo(models.Model):

    jogo = models.ForeignKey(
        JogoPedagogico,
        on_delete=models.CASCADE,
        related_name="galeria"
    )

    titulo = models.CharField(
        max_length=200,
        blank=True
    )

    imagem = models.ImageField(
        upload_to="jogos/galeria/"
    )

    ordem = models.PositiveIntegerField(
        default=1
    )

    class Meta:
        ordering = ["ordem"]

    def __str__(self):
        return self.titulo or self.jogo.titulo


# =====================================================
# VÍDEOS
# =====================================================

class VideoJogo(models.Model):

    jogo = models.ForeignKey(
        JogoPedagogico,
        on_delete=models.CASCADE,
        related_name="videos"
    )

    titulo = models.CharField(
        max_length=200
    )

    url = models.URLField()

    def __str__(self):
        return self.titulo


# =====================================================
# SUGESTÕES
# =====================================================

class SugestaoJogo(models.Model):

    class Status(models.TextChoices):
        NOVO = "novo", "Novo"
        ANALISE = "analise", "Em análise"
        APROVADO = "aprovado", "Aprovado"
        REJEITADO = "rejeitado", "Rejeitado"

    nome_professor = models.CharField(
        max_length=150
    )

    email = models.EmailField(
        blank=True
    )

    escola = models.CharField(
        max_length=150,
        blank=True
    )

    titulo_jogo = models.CharField(
        max_length=200
    )

    descricao = RichTextUploadingField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NOVO
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return self.titulo_jogo