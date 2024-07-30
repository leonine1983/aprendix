from typing import Any
from django import forms
from rh.models import Escola
from gestao_escolar.models import Turmas,Alunos, Remanejamento, Serie_Escolar, Matriculas, TamanhoRoupa

# widget personalizado que usa as classes (form-control, border, p-3, pb-3 e bg-transparent) para ser atribuido ao campo 'tempo_meses' 

escola_fora = {
    ('1','Não recebe'), 
    ('2','Em hospital'),
    ('3', 'Em domicílio')
}

turno = {
    ('1', 'Matutino'),
    ('2', 'Verspertino'),
    ('3', 'Noturno')
}


class Matricula_form(forms.ModelForm):
    
    aluno = forms.ModelChoiceField(
        queryset = Alunos.objects.none() ,
        widget=forms.Select(attrs={'class': 'border border-info pb-1  txt-p col-6 rounded-1'}),
    )
          
    escolarizacao_fora = forms.ChoiceField(
        choices=escola_fora,
        widget=forms.Select(attrs={'class': ' border border-info pb-1 txt-p col rounded-1'}),
        
    )        
    #periodo_multiserie = forms.ChoiceField(
        #choices=turno,
        #widget=forms.Select(attrs={'class': ' border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1'}),
        #required=False          
    #) 
    #data_afastamento_inicio = forms.DateField(
        #widget=forms.DateInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col2 m-2 rounded-1', 'type': 'date'}),      
        #required=False  
        #  )
    #data_afastamento_fim = forms.DateField(
        #widget=forms.DateInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col2 m-2 rounded-1', 'type': 'date'}),      
        #required=False  
        #)
    #motivo_afastamento = forms.CharField(
        #widget=forms.Textarea(attrs={'class': 'border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1 h-25'}),
        #required=False
        #)      
    
    calcula_media = forms.BooleanField(
        label='Não calcular média',
        widget=forms.CheckboxInput(attrs={'class': ' pb-1  txt-p col-3 rounded-1'}),
        required=False
        )   

    turma = forms.ModelChoiceField(
        label='Turma',
        queryset=Turmas.objects.none(),
        widget=forms.Select(attrs={'class': 'border border-info pb-1 txt-p col  rounded-1'}),
    ) 

    serie_multiseriada  = forms.ModelChoiceField(
        queryset = Serie_Escolar.objects.all(),
        widget=forms.Select(attrs={'class': 'border border-info  pb-1 txt-p col rounded-1'}),
        required=False  
    )
    camisa_tamanho  = forms.ModelChoiceField(
        label='Escolha o tamando do uniforme do aluno',
        queryset = TamanhoRoupa.objects.all(),
        widget=forms.Select(attrs={'class': 'border border-info pb-1 txt-p col rounded-1'}),
        required=False  
    )

  
   
    # Para aceitar o modificação do form feita lá na view
    def __init__(self, *args, **kwargs):
        turma_queryset = kwargs.pop('turma_queryset', None)
        aluno_queryset = kwargs.pop ('aluno_query', None)
        super().__init__(*args, **kwargs)

        if turma_queryset is not None:
            self.fields['turma'].queryset = turma_queryset
            self.fields['turma'].initial = turma_queryset.first()
            self.fields['aluno'].queryset = aluno_queryset

        # Dentro do metodo init, iniciaremos o campo serie_multiseriada OCULTA, e        
        # só exiberemos ela se a turma tiver valor true para o campo multiserie

        for n in turma_queryset:            
            if n.turma_multiserie:
                self.fields['serie_multiseriada'].widget = forms.Select(attrs={'class': 'border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1'})
                self.fields['serie_multiseriada'].queryset = Serie_Escolar.objects.all()
            else:
                self.fields['serie_multiseriada'].widget = forms.HiddenInput()
                self.fields['serie_multiseriada'].label = ""
    
    class Meta:
        model = Matriculas
        fields =['aluno',  'turma', 'camisa_tamanho',  'escolarizacao_fora','calcula_media' ,'obervacao','serie_multiseriada',]


class MatriculaUpdate_form(forms.ModelForm):
    
    class Meta:
        model = Matriculas
        fields =['aluno',  'turma', 'camisa_tamanho',  'escolarizacao_fora','calcula_media' ,'obervacao','serie_multiseriada',]
  

class Turma_form(forms.ModelForm):
    
    nome = forms.CharField(
        #label='Nome da Turma:',
        widget=forms.TextInput(attrs={'class': 'form-control border p-3 pb-3 bg-transparent w-100'}),
    )  
    
    class Meta:
        model = Turmas
        fields =['nome']


class Matricula_form_retorno_aluno(forms.ModelForm):
    
    aluno = forms.ModelChoiceField(
        queryset = Alunos.objects.none() ,
        widget=forms.Select(attrs={'class': 'border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1'}),
    )
           
    escolarizacao_fora = forms.ChoiceField(
        choices=escola_fora,
        widget=forms.Select(attrs={'class': ' border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1'}),
        
    )        
    #periodo_multiserie = forms.ChoiceField(
        #choices=turno,
        #widget=forms.Select(attrs={'class': ' border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1'}),
        #required=False          
    #) 
    #data_afastamento_inicio = forms.DateField(
        #widget=forms.DateInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col2 m-2 rounded-1', 'type': 'date'}),      
        #required=False  
        #  )
    #data_afastamento_fim = forms.DateField(
        #widget=forms.DateInput(attrs={'class': 'form-control border border-info p-3 pb-3 bg-transparent text-info col2 m-2 rounded-1', 'type': 'date'}),      
        #required=False  
        #)
    #motivo_afastamento = forms.CharField(
        #widget=forms.Textarea(attrs={'class': 'border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1 h-25'}),
        #required=False
        #)      
    
    calcula_media = forms.BooleanField(
        label='Não calcular média',
        widget=forms.CheckboxInput(attrs={'class': 'border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1'}),
        required=False
        )   

    turma = forms.ModelChoiceField(
        queryset=Turmas.objects.all(),
        widget=forms.Select(attrs={'class': 'border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1'}),
    ) 

    serie_multiseriada  = forms.ModelChoiceField(
        queryset = Serie_Escolar.objects.all(),
        widget=forms.Select(attrs={'class': 'border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1'}),
        required=False  
    )
    obervacao = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1'}),
        required=False  
    )  
    # Para aceitar o modificação do form feita lá na view
    def __init__(self, *args, **kwargs):
        aluno_queryset = kwargs.pop('aluno', None)
        super().__init__(*args, **kwargs)

        if aluno_queryset is not None:
            self.fields['aluno'].queryset = aluno_queryset

        # Dentro do metodo init, iniciaremos o campo serie_multiseriada OCULTA, e        
        # só exiberemos ela se a turma tiver valor true para o campo multiserie        
        self.fields['serie_multiseriada'].widget = forms.Select(attrs={'class': 'border border-info p-2 pb-1 bg-transparent text-info col m-2 rounded-1'})
        self.fields['serie_multiseriada'].queryset = Serie_Escolar.objects.all()
           
    
    class Meta:
        model = Matriculas
        fields =['aluno',  'turma',  'obervacao', 'escolarizacao_fora', 'serie_multiseriada']



