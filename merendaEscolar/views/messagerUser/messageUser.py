"""
views/mensagens.py
==================
View de envio de mensagens via AJAX — compatível com o modal msg_btn_modal.html
Registre a URL em urls.py:

    path('mensagens/enviar/', views.EnviarMensagemView.as_view(), name='mensagem-enviar'),

Busca de usuários (autocomplete):
    path('mensagens/buscar-usuarios/', views.BuscarUsuariosView.as_view(), name='mensagem-buscar-usuarios'),
"""

import json
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST

from core.views.baseNutricionista import BaseNutricionistaView   # sua base
from admin_acessos.models import MessageUser  
from django.db.models import Q       # seu model


class EnviarMensagemView(BaseNutricionistaView, View):
    """
    POST /merenda/mensagens/enviar/
    Aceita: tipo_destinatario, assunto, mensagem[, destinatario_id]
    Retorna: JSON { ok: true, total: N } | { ok: false, erro: '...' }
    """

    http_method_names = ['post']

    def post(self, request, *args, **kwargs):

        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'erro': 'Requisição inválida.'}, status=400)

        tipo       = request.POST.get('tipo_destinatario', '').strip()
        assunto    = request.POST.get('assunto', '').strip()
        mensagem   = request.POST.get('mensagem', '').strip()
        dest_id    = request.POST.get('destinatario_id', '').strip()

        # ── Validações básicas ──────────────────────────────────────────
        if not tipo:
            return JsonResponse({'ok': False, 'erro': 'Destinatário não informado.'})

        if not assunto:
            return JsonResponse({'ok': False, 'erro': 'Assunto obrigatório.'})

        if not mensagem:
            return JsonResponse({'ok': False, 'erro': 'Mensagem não pode estar vazia.'})

        # ── Montar lista de destinatários ───────────────────────────────
        destinatarios = self._resolver_destinatarios(tipo, dest_id)

        if not destinatarios:
            return JsonResponse({'ok': False, 'erro': 'Nenhum destinatário encontrado.'})

        # ── Criar mensagens ─────────────────────────────────────────────
        msgs = [
            MessageUser(
                remetente=request.user,
                destinatario=dest,
                assunto=assunto,
                mensagem=mensagem,
            )
            for dest in destinatarios
            if dest != request.user        # não envia para si mesmo
        ]

        MessageUser.objects.bulk_create(msgs, ignore_conflicts=True)

        return JsonResponse({'ok': True, 'total': len(msgs)})

    # ── helpers ─────────────────────────────────────────────────────────

    def _resolver_destinatarios(self, tipo, dest_id):
        """
        Retorna queryset/lista de Users conforme o tipo selecionado.
        """
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
            return list(
                User.objects
                .filter(is_active=True)
                .exclude(is_superuser=True)   # opcional: excluir superusers
            )

        return []

    @staticmethod
    def _usuarios_do_grupo(nome_grupo):
        try:
            grupo = Group.objects.get(name=nome_grupo)
            return list(grupo.user_set.filter(is_active=True))
        except Group.DoesNotExist:
            return []


# ═══════════════════════════════════════════════════════════════════════════════
# BUSCA DE USUÁRIOS (AUTOCOMPLETE)
# ═══════════════════════════════════════════════════════════════════════════════

class BuscarUsuariosView(BaseNutricionistaView, View):
    """
    GET /admin/acessos/buscar-usuarios/?q=<termo>
    Retorna lista JSON: [{ id, nome, username, grupo }]
    """

    http_method_names = ['get']

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