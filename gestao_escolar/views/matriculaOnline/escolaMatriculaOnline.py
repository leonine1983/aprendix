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

    # Campo 'ano_letivo' - supondo que seja um campo relacionado a um modelo 'Ano'
    ano_letivo = forms.ModelChoiceField(
        queryset=AnoLetivo.objects.all(),  # Seleciona todos os objetos do modelo Ano
        widget=forms.Select(attrs={'class': 'form-class'}),
        required=True,  # Campo obrigatório (se necessário)
        label='Ano Letivo'
    )

    # Campo 'data_inicio' - Data de início
    data_inicio = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'class': 'form-class',
                'type': 'date',
                'placeholder': 'DD/MM/YYYY'
            }
        ),
        input_formats=['%Y-%m-%d'],  # Formato de entrada da data
        required=True  # Campo obrigatório
    )

    # Campo 'data_fim' - Data de fim
    data_fim = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'class': 'form-class',
                'type': 'date',
                'placeholder': 'DD/MM/YYYY'
            }
        ),
        input_formats=['%Y-%m-%d'],  # Formato de entrada da data
        required=True  # Campo obrigatório
    )

    # Campo 'ativo' - Campo Booleano (Ativo/Desativo)
    ativo = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-class'}),
        required=False,  # Não obrigatório (se necessário)
        initial=True,  # Definindo como True por padrão (se necessário)
        label='Ativo'
    )

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')

        # Verificar se a data_fim é posterior à data_inicio
        if data_inicio and data_fim:
            if data_fim < data_inicio:
                raise forms.ValidationError('A data de término não pode ser anterior à data de início.')

        return cleaned_data


from django import forms
class SerieOnlineForm(forms.ModelForm):
    class Meta:
        model = SerieOnline
        fields = [ 'serie', 'turno', 'quantidade_vagas']





# Adicionar nova escola de matrícula online
@login_required
def adicionar_escola(request):
    if request.method == 'POST':
        form = EscolaMatriculaOnlineForm(request.POST)
        if form.is_valid():
            escola = Escola.objects.get(id=request.session['escola_id'])
            
            # Verifica se já existe algum registro ativo para essa escola
            ultimo_registro = EscolaMatriculaOnline.objects.filter(escola=escola, ativo=True).last()
            if ultimo_registro:
                # Se existir, muda o 'ativo' do último registro para False
                ultimo_registro.ativo = False
                ultimo_registro.save()

            # Antes de salvar o formulário, atribuímos a escola
            nova_matricula = form.save(commit=False)  # Não salva imediatamente
            nova_matricula.escola = escola  # Atribui a escola
            nova_matricula.ativo = True  # Define o novo registro como ativo
            nova_matricula.save()  # Agora sim, salva a instância no banco

            messages.success(
                request, 
                "🎉 Período de matrícula online definido com sucesso! 🚀 A escola está pronta para receber novas matrículas via internet."
            )

            return redirect('Gestao_Escolar:adicionar_escola')
    else:
        form = EscolaMatriculaOnlineForm()

    return render(request, 'Escola/inicio.html', {
        'form': form,
        'conteudo_page': "Add Matricula Online",
        'titulo_page': "Definição de Período de Matrícula Online",
        'EscolaMatriculaOnline': EscolaMatriculaOnline.objects.filter(escola=request.session['escola_id'])
    })


# Editar escola de matrícula online
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


