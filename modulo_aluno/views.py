from django.shortcuts import render


# Create your views here.
def home_aluno(request):
    
    return render(request, 'modulo_aluno/base.html')
