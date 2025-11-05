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
        self.fields['sexo'].required = False
        self.fields['etnia'].required = False
        self.fields['nacionalidade'].required = False
        self.fields['cartorio_uf'].required = False

        # 🔒 Deixa o campo bairro desativado
        if 'bairro' in self.fields:
            self.fields['bairro'].widget.attrs['disabled'] = True
            self.fields['bairro'].widget.attrs['class'] = 'form-control'
            self.fields['cidade'].widget.attrs['disabled'] = True
            self.fields['cidade'].widget.attrs['class'] = 'form-control'
            self.fields['estado'].widget.attrs['disabled'] = True
            self.fields['estado'].widget.attrs['class'] = 'form-control'
            self.fields['rua'].widget.attrs['disabled'] = True
            self.fields['rua'].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        senha_repeat = cleaned_data.get("senha_repeat")

        if senha and senha != senha_repeat:
            self.add_error('senha_repeat', "As senhas não coincidem.")
