from django.shortcuts import render, redirect
from gestao_escolar.models import Alunos
from .matricualOnline_form import MatriculaOnline_etapa1
from django.contrib.auth.models import User, Group
from django.contrib import messages



def cadastro_aluno_etapa1_exibeSenha(request, aluno_id):
    aluno = Alunos.objects.get(id = aluno_id)       
    return render(request, 'Escola/matriculaOnline/etapa1_exibeSenha.html', {'aluno':aluno})

