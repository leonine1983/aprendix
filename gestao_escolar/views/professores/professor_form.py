from django import forms
from rh.models import Escola
from gestao_escolar.models import Turmas, Matriculas
from rh.models import Pessoas, Vinculo_empregaticio, Ano, Contrato, Profissao, Encaminhamentos

# widget personalizado que usa as classes (form-control, border, p-3, pb-3 e bg-transparent) para ser atribuido ao campo 'tempo_meses' 

# 1º Esse
class Pessoa_form(forms.ModelForm):   
    nome = forms.CharField(
        label="Nome do Professor",
        widget=forms.TextInput(attrs={'class': "border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1"})
    )
    sobrenome = forms.CharField(
        label="Sobrenome do Professor",
        widget=forms.TextInput(attrs={'class': "border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1"})
    )
  
    data_nascimento = forms.DateField(
        label='Data de Nascimento:',
        widget=forms.DateInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col2 m-2 rounded-1', 'type': 'date'}),        
    )
    cpf= forms.CharField(
        label="Nº do CPF",
        widget=forms.TextInput(attrs={'class': "border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1"})
    )
    rg= forms.CharField(
        label="Nº do RG",
        widget=forms.TextInput(attrs={'class': "border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1"})
    )
    rua= forms.CharField(
        label=" Nome da Rua",
        widget=forms.TextInput(attrs={'class': "border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1"})
    )
    complemento= forms.CharField(
        label="Complemento",
        widget=forms.TextInput(attrs={'class': "border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1"})
    )
    rg= forms.CharField(
        label="Nº do RG",
        widget=forms.TextInput(attrs={'class': "border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1"})
    )
    numero_casa= forms.CharField(
        label="Nº da casa (ou SN)",
        widget=forms.TextInput(attrs={'class': "border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1"})
    )
    bairro= forms.CharField(
        label="Bairro",
        widget=forms.TextInput(attrs={'class': "border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1"})
    )
    cidade= forms.CharField(
        label="Cidade onde mora",
        widget=forms.TextInput(attrs={'class': "border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1"})
    )
    cep= forms.CharField(
        label="CEP",
        widget=forms.TextInput(attrs={'class': "border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1"})
    )

    class Meta:
        model = Pessoas
        fields = ['nome', 'sobrenome', "data_nascimento", 'nome_profissao', 'cpf', 'rg', 'numero_casa', 'bairro', 'cidade', 'cep']


# Pessoa_Vinculo_FORM---------------------------------------------------------------------------------------
choice_vinculo = {
    ("contrato" , "Contrato"),
    ("decreto" , "Decreto"),
    ("efetivo" , "Efetivo"),
    ("estagio" , "Estágio"),
}

# 2º Esse. Apos criar o registro da pessoa é direcionado para definir o tipo de vinculo (contrato, estagio, decrecto ou efetivo)

class Create_Pessoa_Vinculo_FORM(forms.ModelForm):

    pessoa = forms.ModelChoiceField(
        queryset= Pessoas.objects.none(),        
        widget=forms.Select(attrs={'class': 'p-2 pb-1 bg-transparent text-light col m-2 rounded-1 text-uppercase '}),        
    )
    vinculo = forms.ChoiceField(
        choices = choice_vinculo,        
        widget=forms.Select(attrs={'class': "border border-info p-2 pb-1 bg-light text-muted  col m-2 rounded-1"})
    ) 
    ano = forms.ModelChoiceField (
        queryset=Ano.objects.all(),      
        widget=forms.Select(attrs={'class': "border border-info p-2 pb-1 bg-light text-muted  col m-2 rounded-1"})
    )

    def __init__(self, *args, **kwargs):
        pessoa_queryset = kwargs.pop('pessoa', None)
        super().__init__(*args, **kwargs)

        if pessoa_queryset is not None:
            self.fields['pessoa'].queryset = pessoa_queryset
            self.fields['pessoa'].initial = pessoa_queryset.first()

    class Meta:
        model = Vinculo_empregaticio
        fields = ['pessoa', 'vinculo', 'ano']


# Contrato_form --------------------------------------------------------------------------------
class Contrato_form(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = ['contratado', 'ano_contrato', 'nome_profissao', 'nome_escola']
    
    contratado = forms.ModelChoiceField(
        label='Nome do profissional:',
        queryset=Pessoas.objects.none(),  # Query to fetch all Pessoas objects
        widget=forms.Select(attrs={'class': ' p-1 mb-3 bg-transparent'}),
    )
    ano_contrato = forms.ModelChoiceField(
        label='Ano:',
        queryset=Ano.objects.none(),  # Query to fetch all Ano objects
        widget=forms.Select(attrs={'class': 'border p-1 mb-3 bg-transparent'}),
    )  
    nome_escola = forms.ModelChoiceField(
        label='Escola',
        queryset=Escola.objects.all(),  # Query to fetch all Ano objects
        widget=forms.Select(attrs={'class': 'border p-1 mb-3 bg-transparent'}),
    )    
    nome_profissao = forms.ModelChoiceField(
        label='Defina a função que o profissional irá desempenhar na escola. Deve escolher somente uma:',
        queryset=Profissao.objects.all(),  # Query to fetch all Ano objects
        widget=forms.Select(attrs={'class': 'border p-1 mb-3 bg-light text-muted'}),
    )
    

    def __init__(self, *args, **kwargs):
        pessoa_query = kwargs.pop('pessoa', None)
       #vinculo_query = kwargs.pop('vinculo', None)
        ano_query = kwargs.pop('ano', None)
        escola_query = kwargs.pop('escola', None)
        super().__init__(*args, **kwargs)

        if pessoa_query is not None:
            self.fields['contratado'].queryset = pessoa_query
            self.fields['contratado'].initial = pessoa_query.first()
            self.fields['ano_contrato'].queryset = ano_query
            self.fields['ano_contrato'].initial = ano_query.first()
            self.fields['nome_escola'].queryset = escola_query
            self.fields['nome_escola'].initial = escola_query.first()


# Pessoa_Vinculo_FORM---------------------------------------------------------------------------------------
class Professor_form(forms.ModelForm):

    escolas = forms.CharField()
    data_entrada_escola = forms.CharField()
    data_saida_escola = forms.CharField()
    efetivo = forms.CharField()
    # ---------------------------------------------    
    disciplina = forms.CharField()
    formacao_academica = forms.CharField()
    instituto_academico = forms.CharField()
    foto = forms.CharField()

    description = forms.CharField(
        label='Descreva o motivo do Remanejamento. Ex.: Escola para onde o aluno será remanejado e o porquê.',        
        widget=forms.Textarea(attrs={'class': 'border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1'}),
    )    


class Turma_form(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)  # Obtém o request passado como argumento
        super().__init__(*args, **kwargs)
        
        # Use o request para filtrar o queryset
        if request:
            self.fields['turma'].queryset = Turmas.objects.filter(
                ano_letivo=request.session.get('anoLetivo_id'),
                escola=request.session.get('escola_nome')
            )

    class Meta:
        model = Matriculas
        fields =['turma']



 
# Form do Encaminhamento ---------------------------------------------------------
class Create_Pessoa_Encaminhamento_form(forms.ModelForm):
    class Meta:
        model = Encaminhamentos
        fields = ['encaminhamento', 'destino', 'profissao']
    
    encaminhamento = forms.ModelChoiceField(
        label='Profissional a ser encaminhado:',
        queryset=Contrato.objects.none(),  # Query to fetch all Pessoas objects
        widget=forms.Select(attrs={'class': 'border border-verde-desgastado p-1 mb-3 bg-transparent  text-light text-uppercase fs-6'}),
    )
    destino = forms.ModelChoiceField(
        label='Encaminhado para:',
        queryset=Escola.objects.none(),  # Query to fetch all Pessoas objects
        widget=forms.Select(attrs={'class': 'border border-verde-desgastado p-1 mb-3 bg-transparent  text-light text-uppercase fs-6'}),
    )
    profissao = forms.ModelChoiceField(
        label='Atividade profissional:',
        queryset=Profissao.objects.none(),  # Query to fetch all Pessoas objects
        widget=forms.Select(attrs={'class': 'border border-verde-desgastado p-1 mb-3 bg-transparent  text-light text-uppercase fs-6'}),
    )

    def __init__(self, *args, **kwargs):
        encaminhamento_query = kwargs.pop('encaminhamento', None)
        destino_query =kwargs.pop('destino', None)
        profissao_query = kwargs.pop('profissao', None)
        super().__init__(*args, **kwargs)

        if encaminhamento_query is not None:
            self.fields['encaminhamento'].queryset = encaminhamento_query            
            self.fields['encaminhamento'].initial = encaminhamento_query.first()
            self.fields['destino'].queryset = destino_query            
            self.fields['destino'].initial = destino_query.first()
            self.fields['profissao'].queryset = profissao_query
            self.fields['profissao'].initial = profissao_query.first()
   

