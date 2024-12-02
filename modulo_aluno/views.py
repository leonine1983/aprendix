from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def home_aluno(request):
    
    return render(request, 'modulo_aluno/base.html')
