from django import forms
from django.contrib.auth import get_user_model
from core.models.perfil import PerfilUsuario

User = get_user_model()

class PerfilForm(forms.ModelForm):
    first_name = forms.CharField(label="Nome")
    last_name = forms.CharField(label="Sobrenome")
    email = forms.EmailField(label="E-mail")

    class Meta:
        model = PerfilUsuario
        fields = ["telefone", "cargo"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

        self.fields["first_name"].initial = user.first_name
        self.fields["last_name"].initial = user.last_name
        self.fields["email"].initial = user.email

        self.user = user

    def save(self, commit=True):
        perfil = super().save(commit=False)

        self.user.first_name = self.cleaned_data["first_name"]
        self.user.last_name = self.cleaned_data["last_name"]
        self.user.email = self.cleaned_data["email"]

        if commit:
            self.user.save()
            perfil.save()

        return perfil