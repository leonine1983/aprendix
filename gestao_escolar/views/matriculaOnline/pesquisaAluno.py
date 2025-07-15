from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from gestao_escolar.models import Alunos, MatriculasOnline
from django.db.models import Q
from gestao_escolar.views.alunos.partials_alunos.alunos_form import Alunos_form
from django.contrib import messages

def pesquisar_aluno(request):
    form = Alunos_form(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        nome = form.cleaned_data.get('nome_completo', '').strip()
        nome_mae = form.cleaned_data.get('nome_mae', '').strip()    
        CPF_mae = form.cleaned_data.get('CPF_mae', '').strip()

        alunos = Alunos.objects.filter(
            Q(nome_completo__icontains=nome) &
            Q(nome_mae__icontains=nome_mae) &
            Q(CPF_mae__icontains=CPF_mae) 
        )

        if alunos.exists():
            return render(request, 'Escola/matriculaOnline/resultados_aluno.html', {'alunos': alunos})
        else:            
            return redirect(reverse_lazy('Gestao_Escolar:cadastro_aluno_etapa1', kwargs={'nome': nome, 'mae':nome_mae, 'cpf':CPF_mae}))
        
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f'{error}')
 

    return render(request, 'Escola/matriculaOnline/pesquisar_aluno.html', {'form':form})
