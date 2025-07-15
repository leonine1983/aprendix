

from django import forms
from .views import *
from ckeditor.fields import RichTextField

class MessageUserForm(forms.ModelForm):
    class Meta:        
        model = message_user
        fields = ['user', 'assunto', 'messagem']  # Mantenha 'messagem' se esse é o nome real no modelo
        widgets = {
            'remetente': forms.HiddenInput,
            'messagem': RichTextField()
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(MessageUserForm, self).__init__(*args, **kwargs)
        
        if user:
            self.fields['remetente'].initial = self.request.user
