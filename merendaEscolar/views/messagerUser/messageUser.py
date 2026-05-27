# views/mensagens.py

import json
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.db.models import Q

from admin_acessos.models import MessageUser


class EnviarMensagemView(LoginRequiredMixin, View):
    """
    POST /merenda/mensagens/enviar/
    """

    def post(self, request, *args, **kwargs):

        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'erro': 'Requisição inválida.'}, status=400)

        tipo    = request.POST.get('tipo_destinatario', '').strip()
        assunto = request.POST.get('assunto', '').strip()
        mensagem = request.POST.get('mensagem', '').strip()
        dest_id  = request.POST.get('destinatario_id', '').strip()

        if not tipo:
            return JsonResponse({'ok': False, 'erro': 'Destinatário não informado.'})
        if not assunto:
            return JsonResponse({'ok': False, 'erro': 'Assunto obrigatório.'})
        if not mensagem:
            return JsonResponse({'ok': False, 'erro': 'Mensagem não pode estar vazia.'})

        destinatarios = self._resolver_destinatarios(tipo, dest_id)

        if not destinatarios:
            return JsonResponse({'ok': False, 'erro': 'Nenhum destinatário encontrado.'})

        msgs = [
            MessageUser(
                remetente=request.user,
                destinatario=dest,
                assunto=assunto,
                mensagem=mensagem,
            )
            for dest in destinatarios
            if dest != request.user
        ]

        if not msgs:
            return JsonResponse({'ok': False, 'erro': 'Nenhuma mensagem a enviar (você seria o único destinatário).'})

        criados = MessageUser.objects.bulk_create(msgs, ignore_conflicts=True)

        return JsonResponse({'ok': True, 'total': len(criados)})

    def _resolver_destinatarios(self, tipo, dest_id):
        if tipo == 'individual':
            try:
                return [User.objects.get(pk=dest_id, is_active=True)]
            except (User.DoesNotExist, ValueError):
                return []
        elif tipo == 'grupo_nutricionista':
            return self._usuarios_do_grupo('Nutricionista')
        elif tipo == 'grupo_merendeira':
            return self._usuarios_do_grupo('Merendeira')
        elif tipo == 'todos':
            return list(User.objects.filter(is_active=True).exclude(is_superuser=True))
        return []

    @staticmethod
    def _usuarios_do_grupo(nome_grupo):
        try:
            grupo = Group.objects.get(name=nome_grupo)
            return list(grupo.user_set.filter(is_active=True))
        except Group.DoesNotExist:
            return []


class BuscarUsuariosView(LoginRequiredMixin, View):
    """
    GET /merenda/mensagens/buscar-usuarios/?q=<termo>
    """

    def get(self, request, *args, **kwargs):
        q = request.GET.get('q', '').strip()

        if len(q) < 2:
            return JsonResponse([], safe=False)

        users = (
            User.objects
            .filter(is_active=True)
            .filter(
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q)  |
                Q(username__icontains=q)
            )
            .prefetch_related('groups')
            [:20]
        )

        resultado = [
            {
                'id':       u.pk,
                'nome':     u.get_full_name() or u.username,
                'username': u.username,
                'grupo':    u.groups.first().name if u.groups.exists() else 'Sem grupo',
            }
            for u in users
        ]

        return JsonResponse(resultado, safe=False)