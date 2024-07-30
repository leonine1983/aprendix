from django.shortcuts import redirect
from django.urls import reverse


from django.shortcuts import redirect, reverse

# Define um decorador chamado verifica_sessoes, que aceita uma função de visualização (view_func) como argumento
def verifica_sessoes(view_func):
    # Define uma função interna chamada wrapper que recebe request e quaisquer argumentos adicionais
    def wrapper(request, *args, **kwargs):
        # Verifica se o usuário está autenticado
        if request.user.is_authenticated:
            # Verifica se 'anoLetivo_id' e 'escola_nome' estão presentes na sessão do usuário
            if 'anoLetivo_id' not in request.session or 'escola_nome' not in request.session:
                # Se não estiverem presentes, redireciona o usuário para a página de início
                return redirect(reverse('Gestao_Escolar:GE_inicio'))  
        # Retorna a função de visualização original com o request e quaisquer argumentos adicionais
        return view_func(request, *args, **kwargs)
    # Retorna a função interna wrapper
    return wrapper
