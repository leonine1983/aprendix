from django.db import models
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from django.db.models.signals import post_migrate
from ckeditor.fields import RichTextField
from rh.models import Pessoas

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


@receiver(post_migrate)
def setup_post_migrate(sender, **kwargs):
    if sender.name == 'admin_acessos':
        if not MessageUser.objects.exists():
            for user in User.objects.all():
                MessageUser.objects.get_or_create(
                    destinatario=user,
                    assunto="Olá!",
                    mensagem="Bem-vindo ao nosso sistema!",
                )

    if not NomeclaturaJanelas.objects.exists():
        NomeclaturaJanelas.objects.get_or_create(
            nome_disciplina='Objetos da Aprendizagem/Disciplinas',
            notas='Notas do Aluno'
        )
    
    # Adicionar ou modificar grupos se necessário
    group_names = ['Nutricionista', 'Professor', 'Diretor', 'Aluno']
    for group_name in group_names:
        Group.objects.get_or_create(name=group_name)



    
"""
from rh.models import Escola, Ano
class ConfigAvisos(models.Model):
    escola = models.ForeignKey(Escola, related_name="AvisoEscola_related", on_delete=models.CASCADE)
    anoLetivo = models.ForeignKey(Ano, related_name='AvisoAnoLetivo_related', on_delete=models.CASCADE)
    decreto_diretor = models.ForeignKey()
"""