from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from gestao_escolar.models import EscolaMatriculaOnline, AnoLetivo, SerieOnline
from django.contrib.auth.decorators import login_required
from rh.models import Escola
from django import forms
from django.contrib import messages


from django import forms

class EscolaMatriculaOnlineForm(forms.ModelForm):
    class Meta:
        model = EscolaMatriculaOnline
        fields = ['ano_letivo', 'data_inicio', 'data_fim', 'ativo']

    ano_letivo = forms.ModelChoiceField(
        queryset=AnoLetivo.objects.none(),  # inicializa vazio
        widget=forms.Select(attrs={'class': 'form-class'}),
        required=True,
        label='Ano Letivo'
    )

    data_inicio = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'class': 'form-class',
                'type': 'date',
                'placeholder': 'DD/MM/YYYY'
            }
        ),
        input_formats=['%Y-%m-%d'],
        required=True
    )

    data_fim = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'class': 'form-class',
                'type': 'date',
                'placeholder': 'DD/MM/YYYY'
            }
        ),
        input_formats=['%Y-%m-%d'],
        required=True
    )

    ativo = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-class'}),
        required=False,
        initial=True,
        label='Ativo'
    )

    def __init__(self, *args, **kwargs):
        ano_atual = kwargs.pop("ano_atual", None)  # recebo o ano_atual da view
        super().__init__(*args, **kwargs)

        if ano_atual:
            # só mostra anos posteriores ao atual
            self.fields['ano_letivo'].queryset = AnoLetivo.objects.filter(ano__gt=ano_atual)
        else:
            # fallback se não tiver ano atual
            self.fields['ano_letivo'].queryset = AnoLetivo.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')

        if data_inicio and data_fim and data_fim < data_inicio:
            raise forms.ValidationError('A data de término não pode ser anterior à data de início.')

        return cleaned_data



from django import forms
class SerieOnlineForm(forms.ModelForm):
    class Meta:
        model = SerieOnline
        fields = [ 'serie', 'turno', 'quantidade_vagas']

@login_required
def adicionar_escola(request):
    anol = request.session.get('anoLetivo_nome', None)  
    escola = Escola.objects.get(id=request.session['escola_id'])
    ano = None
    if anol:
        try:
            ano = AnoLetivo.objects.get(ano=anol).ano
        except AnoLetivo.DoesNotExist:
            ano = None

    if request.method == 'POST':
        form = EscolaMatriculaOnlineForm(request.POST, ano_atual=ano)
        if form.is_valid():
            
            ultimo_registro = EscolaMatriculaOnline.objects.filter(escola=escola, ativo=True).last()
            if ultimo_registro:
                ultimo_registro.ativo = False
                ultimo_registro.save()

            nova_matricula = form.save(commit=False)
            nova_matricula.escola = escola
            nova_matricula.ativo = True
            nova_matricula.save()

            messages.success(request, "🎉 Período de matrícula online definido com sucesso! 🚀")
            return redirect('Gestao_Escolar:adicionar_escola')
    else:
        form = EscolaMatriculaOnlineForm(ano_atual=ano)


    return render(request, 'Escola/inicio.html', {
        'form': form,
        'conteudo_page': "Add Matricula Online",
        'titulo_page': "Definição de Período de Matrícula Online",
        'EscolaMatriculaOnline': EscolaMatriculaOnline.objects.filter(escola=request.session['escola_id'])
    })


# Editar escola de matrícula online
@login_required
def editar_escola(request, pk):
    escola = get_object_or_404(EscolaMatriculaOnline, pk=pk)
    if request.method == 'POST':
        form = EscolaMatriculaOnlineForm(request.POST, instance=escola)
        if form.is_valid():
            form.save()
            return redirect('lista_escolas')
    else:
        form = EscolaMatriculaOnlineForm(instance=escola)
    return render(request, 'escolas/editar_escola.html', {'form': form})

# Deletar escola de matrícula online
@login_required
def deletar_escola(request, pk):
    escola = get_object_or_404(EscolaMatriculaOnline, pk=pk)
    escola.delete()
    return redirect('lista_escolas')




# Listar as séries online

# Adicionar nova série online
@login_required
def adicionar_serie(request, pk):
    #'escola',
    if request.method == 'POST':
        form = SerieOnlineForm(request.POST)
        escola = EscolaMatriculaOnline.objects.get(id=pk)
        if form.is_valid():
            novaSerie = form.save(commit=False)
            novaSerie.escola = escola
            form.save()
            # Adiciona uma mensagem de sucesso
            messages.success(
                request, 
                f"✅ Série adicionada com sucesso! 📚 As inscrições online para esta série {novaSerie.serie} {novaSerie.turno} - {novaSerie.quantidade_vagas} vagas, agora estão disponíveis."
            )
            return redirect('Gestao_Escolar:adicionar_escola')
    else:
        form = SerieOnlineForm()
    return render(request, 'Escola/inicio.html', {
        'form': form,        
        'conteudo_page': "Add Series Online",
        'Adiciona_serieTurma': "Add_SeriesTurmas",
        'titulo_page': "Seleciona séries para matrícula online",
    })

# Deletar série online
@login_required
def deletar_serie(request, pk):
    serie = get_object_or_404(SerieOnline, pk=pk)
    serie.delete()

    # Adiciona uma mensagem de sucesso
    messages.success(
        request, 
        "❌ Série excluída com sucesso! 📝 A série não estará mais disponível para matrícula online."
    )

    return redirect('Gestao_Escolar:adicionar_escola')



# Editar série online
@login_required
def editar_serie(request, pk):
    serie = get_object_or_404(SerieOnline, pk=pk)
    if request.method == 'POST':
        form = SerieOnlineForm(request.POST, instance=serie)
        if form.is_valid():
            form.save()
            return redirect('Gestao_Escolar:adicionar_escola')
    else:
        form = SerieOnlineForm(instance=serie)
    return render(request, 'series/editar_serie.html', {'form': form})


