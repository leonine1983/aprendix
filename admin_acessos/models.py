from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField


class MessageUser(models.Model):
    remetente = models.ForeignKey(User, null=True, on_delete=models.CASCADE, editable=False, verbose_name="Remetente da mensagem", related_name="sent_messages")
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Destinatário da mensagem", related_name="received_messages")
    assunto = models.CharField(max_length=100, verbose_name='Assunto da mensagem')
    mensagem = RichTextField(null=True, blank=True)
    aberta = models.BooleanField(default=False)
    foi_consultado = models.BooleanField(default=False)
    data_envio = models.DateTimeField(auto_now_add=True)
    exclude_msg = models.CharField(max_length=5, blank=True, null=True)  # Corrigido para permitir valores em branco

    class Meta:
        ordering = ["-data_envio"]
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"

    def __str__(self) -> str:
        return self.assunto


class PaletaCores(models.Model):
    nome_paleta = models.CharField(max_length=20, default='Paleta Branca')
    cor_primaria = models.CharField(max_length=7, default='#fff')
    cor_secundaria = models.CharField(max_length=7, default='#fff')
    cor_sucesso = models.CharField(max_length=7, default='#fff')
    cor_info = models.CharField(max_length=7, default='#fff')
    cor_aviso = models.CharField(max_length=7, default='#fff')
    cor_perigo = models.CharField(max_length=7, default='#ffffff')
    cor_texto = models.CharField(max_length=7, default='#000')

    def __str__(self):
        return self.nome_paleta


class NomeclaturaJanelas(models.Model):
    nome_disciplina = models.CharField(max_length=50, default='')
    notas = models.CharField(max_length=20, default='')

    def __str__(self):
        return self.nome_disciplina