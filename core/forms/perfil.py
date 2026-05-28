# core/forms/perfil.py

from django import forms
from django.contrib.auth import get_user_model
from core.models.perfil import PerfilUsuario

User = get_user_model()


class PerfilForm(forms.ModelForm):
    """
    Formulário unificado: salva dados do User (first_name, last_name, email)
    e do PerfilUsuario (demais campos) em uma única submissão.
    """

    # ── Campos do User ──────────────────────────────────────────────
    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Primeiro nome"}),
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Sobrenome"}),
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"placeholder": "email@exemplo.com"}),
    )

    class Meta:
        model = PerfilUsuario
        fields = [
            "foto",
            "telefone",
            "cargo",
            "endereco",
            "cidade",
            "estado",
            "cep",
            "graduacao",
            "especializacao",
            "biografia",
            "visibilidade_curriculo",
        ]
        widgets = {
            "foto": forms.ClearableFileInput(),
            "telefone": forms.TextInput(attrs={"placeholder": "(00) 00000-0000"}),
            "cargo": forms.TextInput(attrs={"placeholder": "Ex.: Nutricionista Escolar"}),
            "endereco": forms.TextInput(attrs={"placeholder": "Rua, número, complemento"}),
            "cidade": forms.TextInput(attrs={"placeholder": "Cidade"}),
            "estado": forms.TextInput(attrs={"placeholder": "UF"}),
            "cep": forms.TextInput(attrs={"placeholder": "00000-000"}),
            "graduacao": forms.TextInput(attrs={"placeholder": "Ex.: Nutrição – UFBA"}),
            "especializacao": forms.TextInput(attrs={"placeholder": "Ex.: Saúde Pública – FIOCRUZ"}),
            "biografia": forms.Textarea(attrs={"rows": 4, "placeholder": "Breve apresentação profissional…"}),
            "visibilidade_curriculo": forms.Select(),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = user

        # Pré-popula campos do User a partir da instância
        if user:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial  = user.last_name
            self.fields["email"].initial      = user.email

    def save(self, commit=True):
        perfil = super().save(commit=False)

        # Persiste campos do User
        if self._user:
            self._user.first_name = self.cleaned_data.get("first_name", "")
            self._user.last_name  = self.cleaned_data.get("last_name", "")
            self._user.email      = self.cleaned_data.get("email", "")
            if commit:
                self._user.save(update_fields=["first_name", "last_name", "email"])

        if commit:
            perfil.save()

        return perfil