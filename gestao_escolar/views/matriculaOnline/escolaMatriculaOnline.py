from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from gestao_escolar.models import EscolaMatriculaOnline
from gestao_escolar.models import SerieOnline
from django import forms


class EscolaMatriculaOnlineForm(forms.ModelForm):
    class Meta:
        model = EscolaMatriculaOnline
        fields = ['escola', 'ano_letivo', 'data_inicio', 'data_fim', 'ativo']

from django import forms
class SerieOnlineForm(forms.ModelForm):
    class Meta:
        model = SerieOnline
        fields = ['escola', 'serie', 'turno', 'quantidade_vagas', 'vagas_disponiveis']




# Listar as escolas de matrícula online
def lista_escolas(request):
    escolas = EscolaMatriculaOnline.objects.all()
    return render(request, 'escolas/lista_escolas.html', {'escolas': escolas})

# Adicionar nova escola de matrícula online
def adicionar_escola(request):
    if request.method == 'POST':
        form = EscolaMatriculaOnlineForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_escolas')
    else:
        form = EscolaMatriculaOnlineForm()
    return render(request, 'Escola/matriculaOnline/escolaMatriculaOnline/adicionar_escola.html', {'form': form})

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
def lista_series(request):
    series = SerieOnline.objects.all()
    return render(request, 'series/lista_series.html', {'series': series})

# Adicionar nova série online
def adicionar_serie(request):
    if request.method == 'POST':
        form = SerieOnlineForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_series')
    else:
        form = SerieOnlineForm()
    return render(request, 'series/adicionar_serie.html', {'form': form})

# Editar série online
def editar_serie(request, pk):
    serie = get_object_or_404(SerieOnline, pk=pk)
    if request.method == 'POST':
        form = SerieOnlineForm(request.POST, instance=serie)
        if form.is_valid():
            form.save()
            return redirect('lista_series')
    else:
        form = SerieOnlineForm(instance=serie)
    return render(request, 'series/editar_serie.html', {'form': form})

# Deletar série online
def deletar_serie(request, pk):
    serie = get_object_or_404(SerieOnline, pk=pk)
    serie.delete()
    return redirect('lista_series')

