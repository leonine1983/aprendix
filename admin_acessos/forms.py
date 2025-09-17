
from django import forms
from .models import MessageUser
from ckeditor.widgets import CKEditorWidget

class MessageUserForm(forms.ModelForm):
    class Meta:
        model = MessageUser
        fields = ['destinatario', 'assunto', 'mensagem']
        widgets = {
            'mensagem': CKEditorWidget(),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request:
            self.fields['remetente'].initial = self.request.user



from django.contrib.auth.models import User
from .models import AtualizacaoNotificacao
from ckeditor.widgets import CKEditorWidget

class NotificacaoForm(forms.Form):
    titulo = forms.CharField(max_length=200, label="Título")
    mensagem = forms.CharField(widget=CKEditorWidget(), required=False, label="Mensagem")
    tipo = forms.ChoiceField(choices=AtualizacaoNotificacao.TIPO_CHOICES, label="Tipo de Notificação")
    user = forms.ModelChoiceField(queryset=User.objects.all(), required=False, label="Usuário (opcional, deixa em branco para todos)")

