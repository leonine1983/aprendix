from typing import Any
from controle_estoque.models import ProgramacaoSaidaEstoque, Movimentacao_Estoque
#from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django.contrib.auth.models import User

class Program_saida_form (forms.ModelForm):
    class Meta:
        model = ProgramacaoSaidaEstoque
        fields = '__all__'


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        movimento = Movimentacao_Estoque.objects.filter(tipo = 'saida')
        choices = [(movi.id, f"{movi.quantidade} {movi.unidadeMedida} de {str(movi.alimento.nome).upper()} - {movi.local_destino}") for movi in movimento]
        self.fields['movimentacoes_estoque'].choices = choices
        
       


"""
qp655606683br
 # Envie para o select o nome do produto e a sua quantidade disponivel
        alimento_queryset = Alimentos.objects.filter(quantidade_disponivel__gte=1)
        choices = [(alimento.id, f"{(str(alimento.nome).upper())} - Quant. disponível: {alimento.quantidade_disponivel}{alimento.unidade}") for alimento in alimento_queryset]
        self.fields['alimento'].choices = choices
        # Remove a opçaõ 1 (catina geral) das opções do select        
        self.fields['local_destino'].queryset = self.fields['local_destino'].queryset.exclude(id=1)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].initial = 'entrada'        
        self.fields['local_destino'].initial = '1'
        self.fields['local_destino'].default = 1
        self.fields['local_destino'].required = False
        # Remove a opçaõ 1 (catina geral) das opções do select
        self.fields['fornecedor_alimento'].queryset = self.fields['fornecedor_alimento'].queryset.exclude(id=1)

   """    