from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.functional import cached_property
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DeleteView, ListView

from core.permissions import GroupRequiredMixin
from core.groups.merenda import MERENDEIRA_GROUPS
from core.models.perfil import PerfilUsuario
from core.models import ConfiguraPessoal

from admin_acessos.models import AtualizacaoNotificacaoSistema, NotificacaoProduto


class BaseMerendeiraView(LoginRequiredMixin, GroupRequiredMixin):

    group_required = MERENDEIRA_GROUPS
    login_url = "login"

    # ─────────────────────────────────────────────
    # 🔐 CONTROLE DE GRUPO
    # ─────────────────────────────────────────────

    @cached_property
    def _usuario_eh_merendeira(self):
        return self.request.user.groups.filter(
            name__in=MERENDEIRA_GROUPS
        ).exists()

    # ─────────────────────────────────────────────
    # 📌 DADOS BASE (OTIMIZADOS)
    # ─────────────────────────────────────────────

    @cached_property
    def perfil(self):
        return (
            PerfilUsuario.objects
            .select_related("escola")
            .filter(user=self.request.user)
            .first()
        )

    @cached_property
    def escola_usuario(self):
        """
        Mantém compatibilidade com versão antiga
        """
        return getattr(self.perfil, "escola", None)

    @cached_property
    def nome_escola(self):
        return getattr(self.escola_usuario, "nome", None)

    @cached_property
    def configuracao(self):
        config, _ = ConfiguraPessoal.objects.get_or_create(pk=1)
        return config

    @cached_property
    def grupos_usuario(self):
        return list(self.request.user.groups.values_list("name", flat=True))

    @cached_property
    def usuario_nome(self):
        user = self.request.user
        return user.get_full_name() or user.username

    # ─────────────────────────────────────────────
    # 🔔 NOTIFICAÇÕES (PROTEGIDAS)
    # ─────────────────────────────────────────────

    @cached_property
    def notificacoes_sistema_nao_lidas(self):
        if not self._usuario_eh_merendeira:
            return AtualizacaoNotificacaoSistema.objects.none()

        return AtualizacaoNotificacaoSistema.objects.filter(
            user=self.request.user, lida=False
        ).order_by("-criada_em")[:20]

    @cached_property
    def notificacoes_sistema_lidas(self):
        if not self._usuario_eh_merendeira:
            return AtualizacaoNotificacaoSistema.objects.none()

        return AtualizacaoNotificacaoSistema.objects.filter(
            user=self.request.user, lida=True
        ).order_by("-criada_em")[:10]

    @cached_property
    def notificacoes_produto_nao_lidas(self):
        if not self._usuario_eh_merendeira:
            return NotificacaoProduto.objects.none()

        return NotificacaoProduto.objects.filter(
            usuario=self.request.user, lida=False
        ).select_related("escola").order_by("-criado_em")[:20]

    @cached_property
    def notificacoes_produto_lidas(self):
        if not self._usuario_eh_merendeira:
            return NotificacaoProduto.objects.none()

        return NotificacaoProduto.objects.filter(
            usuario=self.request.user, lida=True
        ).select_related("escola").order_by("-criado_em")[:10]

    # ─────────────────────────────────────────────
    # 🧠 AGREGAÇÃO
    # ─────────────────────────────────────────────

    def _get_data_notificacao(self, obj):
        return getattr(obj, "criada_em", None) or getattr(obj, "criado_em", None)

    @cached_property
    def notificacoes_nao_lidas(self):
        if not self._usuario_eh_merendeira:
            return []

        lista = list(self.notificacoes_sistema_nao_lidas) + list(self.notificacoes_produto_nao_lidas)

        return sorted(lista, key=lambda x: self._get_data_notificacao(x) or 0, reverse=True)[:30]

    @cached_property
    def notificacoes_lidas(self):
        if not self._usuario_eh_merendeira:
            return []

        lista = list(self.notificacoes_sistema_lidas) + list(self.notificacoes_produto_lidas)

        return sorted(lista, key=lambda x: self._get_data_notificacao(x) or 0, reverse=True)[:20]

    # ─────────────────────────────────────────────
    # 🚨 SISTEMA DE MENSAGENS
    # ─────────────────────────────────────────────

    def _ja_existe_mensagem(self):
        return any(messages.get_messages(self.request))

    def _msg(self, nivel, texto):
        if not self._ja_existe_mensagem():
            messages.add_message(self.request, nivel, texto)

    def form_valid(self, form):
        response = super().form_valid(form)

        if isinstance(self, CreateView):
            self._msg(messages.SUCCESS, "Registro incluído com sucesso no sistema.")
        elif isinstance(self, UpdateView):
            self._msg(messages.SUCCESS, "Atualização realizada com sucesso.")

        return response

    def form_invalid(self, form):
        self._msg(
            messages.ERROR,
            "Não foi possível concluir a operação. Verifique os dados informados."
        )
        return super().form_invalid(form)

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)

        if not self._ja_existe_mensagem():
            messages.success(request, "Registro excluído com sucesso.")

        return response

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        if isinstance(self, ListView):
            chave = f"listview_msg_{self.__class__.__name__}"

            if not request.session.get(chave):
                messages.info(
                    request,
                    "Listagem disponível. Utilize os filtros para localizar informações específicas."
                )
                request.session[chave] = True

        return response

    # ─────────────────────────────────────────────
    # 🌐 CONTEXTO GLOBAL UNIFICADO
    # ─────────────────────────────────────────────

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        ctx.update({

            # 👤 USUÁRIO
            "usuario": user,
            "usuario_nome": self.usuario_nome,

            # 🏫 ESCOLA (COMPATÍVEL COM LEGADO)
            "escola": self.escola_usuario,
            "escola_usuario": self.escola_usuario,
            "nome_escola": self.nome_escola,

            # 👥 GRUPOS
            "grupos_usuario": self.grupos_usuario,
            "grupo_principal": self.grupos_usuario[0] if self.grupos_usuario else "Sem grupo",

            # ⚙️ CONFIG
            "config": self.configuracao,
            "itens_por_pagina": self.configuracao.pagina_CardapiosEscolares,

            # 🔐 CONTROLE
            "usuario_eh_merendeira": self._usuario_eh_merendeira,

            # 🔔 NOTIFICAÇÕES
            "notificacoes_sistema_nao_lidas": self.notificacoes_sistema_nao_lidas,
            "notificacoes_sistema_lidas": self.notificacoes_sistema_lidas,
            "notificacoes_produto_nao_lidas": self.notificacoes_produto_nao_lidas,
            "notificacoes_produto_lidas": self.notificacoes_produto_lidas,
            "notificacoes_nao_lidas": self.notificacoes_nao_lidas,
            "notificacoes_lidas": self.notificacoes_lidas,
            "total_nao_lidas": len(self.notificacoes_nao_lidas),
        })

        return ctx