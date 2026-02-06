from django.shortcuts import render


def sobre_system (request):
    return render(request, 'Controle_Estoque/sobre_system.html', {
        'fabricante' : " CAUAN's Techonology",
        'programador': " Rogério Cerqueira da Silva",
        'email_empresa': " cauans.technology@gmail.com"
    })