from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.utils import timezone
   
from django.contrib.auth import get_user_model
from rh.models import Escola

User = get_user_model()


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


class AtualizacaoNotificacaoSistema(models.Model):
    TIPO_CHOICES = [
        ('info', 'Informação'),
        ('aviso', 'Aviso'),
        ('urgente', 'Urgente'),
        ('atualizado', 'Atualização do Sistema'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes')
    titulo = models.CharField(max_length=200)
    mensagem = RichTextField(null=True, blank=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='info')
    lida = models.BooleanField(default=False)
    criada_em = models.DateTimeField(default=timezone.now)
    atualizada_em = models.DateTimeField(auto_now=True)
    event_key = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['-criada_em']
        verbose_name = 'Notificação de Atualização'
        verbose_name_plural = 'Notificações de Atualizações'

    def __str__(self):
        return f'{self.titulo} - {"Lida" if self.lida else "Não lida"}'    


class NotificacaoProduto(models.Model):

    TIPO_CHOICES = (
        ("ESTOQUE_BAIXO", "Estoque Baixo"),
        ("PRODUTO_VENCENDO", "Produto Vencendo"),
        ("TRANSFERENCIA_ENVIADA", "Transferência Enviada"),
        ("TRANSFERENCIA_RECEBIDA", "Transferência Recebida"),
        ("DIVERGENCIA_ABERTA", "Divergência Aberta"),
    )

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notificacoes_escolas")
    escola = models.ForeignKey(Escola, on_delete=models.CASCADE, null=True, blank=True)

    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()

    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    lida = models.BooleanField(default=False)
    event_key = models.CharField(max_length=255, null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        indexes = [
            models.Index(fields=["usuario", "lida"]),
            models.Index(fields=["tipo"]),
        ]

    def __str__(self):
        return f"{self.titulo} - {self.usuario}"
    


# Anlisar se vale a pena manter ------------------------------------------
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


