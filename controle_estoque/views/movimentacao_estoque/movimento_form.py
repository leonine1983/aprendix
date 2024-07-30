from controle_estoque.models import Movimentacao_Estoque, Escolas_model, Alimentos, Fornecedor
from django.db import models
from django.db.models import Q
from django import forms
from django.forms import HiddenInput
from django.contrib.auth.models import User




class Movimento_Entrada_Form (forms.ModelForm):
    fornecedor_alimento = forms.ModelChoiceField(
        queryset = Fornecedor.objects.all()
    )

    class Meta:
        model = Movimentacao_Estoque
        fields = '__all__'        
        tipo = forms.CharField(required=False)
     

        widgets = {            
            'local_destino': forms.Select(attrs={'disabled':True}),
            'local_destino': HiddenInput(),
            'tipo': HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].initial = 'entrada'        
        self.fields['local_destino'].initial = '1'
        self.fields['local_destino'].default = 1
        self.fields['local_destino'].required = False
        # Remove a opçaõ 1 (catina geral) das opções do select
        self.fields['fornecedor_alimento'].queryset = self.fields['fornecedor_alimento'].queryset.exclude(id=1)
        
       

        


class Movimento_Saida_Form(forms.ModelForm):
    class Meta:
        model = Movimentacao_Estoque
        fields = '__all__'        
        tipo = forms.CharField(required=False)

        widgets = {            
            'fornecedor_alimento': forms.Select(attrs={'disabled':True}),
            'fornecedor_alimento': HiddenInput(),
            'tipo': HiddenInput()
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].initial = 'saida'        
        self.fields['fornecedor_alimento'].initial = '1'
        self.fields['fornecedor_alimento'].default = 1
        self.fields['fornecedor_alimento'].required = False
        # feito um filtro no queryset do campo 'alimento' para incluir apenas os registros com 'quantidade_disponivel' maior ou igual a 1. 
        self.fields['alimento'].queryset = self.fields['alimento'].queryset.filter(Q(quantidade_disponivel__gte = 1))

        # Envie para o select o nome do produto e a sua quantidade disponivel
        alimento_queryset = Alimentos.objects.filter(quantidade_disponivel__gte=1)
        choices = [(alimento.id, f"{(str(alimento.nome).upper())} - Quant. disponível: {alimento.quantidade_disponivel}{alimento.unidade}") for alimento in alimento_queryset]
        self.fields['alimento'].choices = choices
        
         # Recupere o usuário logado
        self.fields['observacoes'].initial = 'Não há observações'
        
        # Defina o nome do usuário logado como valor inicial para o campo "responsável"
        self.fields['responsavel'].initial = f'{user.username} | {user.first_name} {user.last_name}'
        #self.fields['responsavel'].widget.attrs['disabled'] = True
        self.fields['responsavel'].required = False
   

  



    

"""

choices = [(alimento.id, f"{alimento.nome} - Quantidade disponível: {alimento.quantidade_disponivel}") for alimento in queryset]
        self.fields['alimento'].choices = choices

alimento = models.ForeignKey(Alimentos, on_delete=models.CASCADE)    
    fornecedor_alimento = models.ForeignKey(Fornecedor, on_delete=models.PROTECT)
    data_hora = models.DateTimeField(auto_now_add=True)
    escolha = {
        ('entrada' , 'Entrada no estoque central'),
        ('saida' , 'Saída')
    }
    
    tipo = models.CharField(max_length=30, choices=escolha)
    quantidade = models.PositiveBigIntegerField(max_length=10)
    unidadeMedida = models.CharField(choices=medida, max_length=10, verbose_name='Unidade de Medida (kg)')
    local_destino = models.ForeignKey(Escolas_model, on_delete=models.PROTECT)
    documento_referencia = models.CharField(max_length=100)
    responsavel = models.CharField(max_length=100)
    observacoes = models.CharField(max_length=100)





class TriagemEnfermaria_Alergias_UpdateForm(forms.ModelForm):   
     
    conteudo_alergia = forms.CharField(required=False)

    class Meta:
        model = ficha_de_atendimento
        fields = [ 'alergias', 'conteudo_alergia', ]
        labels = {
            'alergias' : 'O paciente possui algum tipo de alergia?',
            'conteudo_alergia': 'Descreva a alergia do paciente'
        }

        widgets = {
            'conteudo_alergia': forms.Textarea(attrs={
                 'rows': 50,
                 'cols':150,
                 }),
            
        }
   """    