from django import forms
from gestao_escolar.models import Alunos

class AlunoPerfilForm(forms.ModelForm):
    senha = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite a senha'}),
        required=False
    )
    senha_repeat = forms.CharField(
        label="Repita a senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repita a senha'}),
        required=False
    )

    class Meta:
        model = Alunos
        exclude = ['login_aluno', 'res_cadastro', 'res_atualiza_cadastro']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Campos opcionais
        opcionais = [
            'sexo', 'etnia', 'nacionalidade', 'cartorio_uf',
            'rua', 'bairro', 'cidade', 'estado',
            'estado_naturalidade', 'cidade_naturalidade'
        ]
        for campo in opcionais:
            if campo in self.fields:
                self.fields[campo].required = False
                self.fields[campo].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        senha_repeat = cleaned_data.get("senha_repeat")

        if senha and senha != senha_repeat:
            self.add_error('senha_repeat', "As senhas não coincidem.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        original = Alunos.objects.get(pk=self.instance.pk)

        # Ignora campos auxiliares
        ignored_fields = ['senha', 'senha_repeat']

        for field, value in self.cleaned_data.items():
            if field in ignored_fields:
                continue  # Ignora campos que não existem no model
            
            if value in [None, '', [], {}]:
                setattr(instance, field, getattr(original, field))

        if commit:
            instance.save()
        return instance
