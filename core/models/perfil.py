# core/models/perfil.py

from django.db import models
from rh.models import Escola
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()

class PerfilUsuario(models.Model):

    VISIBILIDADE_CHOICES = (
        ("privado", "Privado"),
        ("restrito", "Somente usuários autenticados"),
        ("publico", "Público"),
    )

    user = models.OneToOneField(User,  on_delete=models.CASCADE)

    # Identidade
    foto = models.ImageField(upload_to="perfis/fotos/", blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True)
    cargo = models.CharField(max_length=150, blank=True)

    # Endereço
    endereco = models.CharField(max_length=255, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=100, blank=True)
    cep = models.CharField(max_length=15, blank=True)

    # Formação base
    graduacao = models.CharField(max_length=255, blank=True)
    especializacao = models.CharField(max_length=255, blank=True)
    biografia = models.TextField(blank=True)

    escola = models.ForeignKey(
        Escola,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usuarios",
        verbose_name="Escola vinculada"
    )

    # Controle de visibilidade
    visibilidade_curriculo = models.CharField(
        max_length=20,
        choices=VISIBILIDADE_CHOICES,
        default="restrito"
    )

    slug_publico = models.SlugField(
    max_length=150,
    blank=True,
    null=True,   # IMPORTANTE
    unique=False # REMOVA unique por enquanto
)

    atualizado_em = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug_publico:
            self.slug_publico = slugify(self.user.get_full_name() or self.user.username)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Perfil - {self.user.username}"
    


class Formacao(models.Model):
    perfil = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name="formacoes")
    titulo = models.CharField(max_length=255)
    instituicao = models.CharField(max_length=255)
    inicio = models.DateField()
    fim = models.DateField(null=True, blank=True)
    descricao = models.TextField(blank=True)

    class Meta:
        ordering = ["-inicio"]


class Experiencia(models.Model):
    perfil = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name="experiencias")
    cargo = models.CharField(max_length=255)
    instituicao = models.CharField(max_length=255)
    inicio = models.DateField()
    fim = models.DateField(null=True, blank=True)
    descricao = models.TextField(blank=True)

    class Meta:
        ordering = ["-inicio"]



class Curso(models.Model):
    perfil = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name="cursos")
    nome = models.CharField(max_length=255)
    instituicao = models.CharField(max_length=255)
    carga_horaria = models.CharField(max_length=50, blank=True)
    ano = models.IntegerField()


class Publicacao(models.Model):
    perfil = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name="publicacoes")
    titulo = models.CharField(max_length=255)
    revista = models.CharField(max_length=255, blank=True)
    link = models.URLField(blank=True)
    ano = models.IntegerField()


class Livro(models.Model):
    perfil = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name="livros")
    titulo = models.CharField(max_length=255)
    editora = models.CharField(max_length=255, blank=True)
    ano = models.IntegerField()
    isbn = models.CharField(max_length=20, blank=True)