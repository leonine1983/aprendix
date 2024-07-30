from django.http import request
from admin_acessos.models import MessageUser



def message_user_contexto(request):
    contexto = {}
    usuario = request.user    

    if usuario.is_authenticated:
        contexto['usuario'] = MessageUser.objects.filter(destinatario_id=usuario)      
    else:
        contexto['usuario']  = {}
    return contexto
