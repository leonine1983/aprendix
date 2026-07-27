from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.functional import cached_property

from core.permissions import GroupRequiredMixin
from core.groups.secretaria import SECRETARIOS_GROUPS
from core.models.perfil import PerfilUsuario
from core.models import ConfiguraPessoal

from admin_acessos.models import AtualizacaoNotificacaoSistema, NotificacaoProduto


class BaseSecretariosView(LoginRequiredMixin, GroupRequiredMixin):

    group_required = SECRETARIOS_GROUPS
    login_url = "login"

    # ─────────────────────────────────────────────
    # 📌 DADOS BASE (CACHE POR REQUEST)
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
    def configuracao(self):
        config, _ = ConfiguraPessoal.objects.get_or_create(pk=1)
        return config

    @cached_property
    def grupos_usuario(self):
        return list(self.request.user.groups.values_list("name", flat=True))

    # ─────────────────────────────────────────────
    # 🔔 NOTIFICAÇÕES DO SISTEMA
    # ─────────────────────────────────────────────

    @cached_property
    def notificacoes_sistema_nao_lidas(self):
        return (
            AtualizacaoNotificacaoSistema.objects
            .filter(user=self.request.user, lida=False)
            .order_by("-criada_em")[:20]
        )

    @cached_property
    def notificacoes_sistema_lidas(self):
        return (
            AtualizacaoNotificacaoSistema.objects
            .filter(user=self.request.user, lida=True)
            .order_by("-criada_em")[:10]
        )

    # ─────────────────────────────────────────────
    # 🔔 NOTIFICAÇÕES DE PRODUTO
    # ─────────────────────────────────────────────

    @cached_property
    def notificacoes_produto_nao_lidas(self):
        return (
            NotificacaoProduto.objects
            .filter(usuario=self.request.user, lida=False)
            .select_related("escola")
            .order_by("-criado_em")[:20]
        )

    @cached_property
    def notificacoes_produto_lidas(self):
        return (
            NotificacaoProduto.objects
            .filter(usuario=self.request.user, lida=True)
            .select_related("escola")
            .order_by("-criado_em")[:10]
        )

    # ─────────────────────────────────────────────
    # 🧠 NORMALIZAÇÃO DE DATA (CRÍTICO)
    # ─────────────────────────────────────────────

    def _get_data_notificacao(self, obj):
        """
        Normaliza timestamp entre models diferentes
        """
        return getattr(obj, "criada_em", None) or getattr(obj, "criado_em", None)

    # ─────────────────────────────────────────────
    # 🔗 AGREGAÇÃO (VISÃO GLOBAL)
    # ─────────────────────────────────────────────

    @cached_property
    def notificacoes_nao_lidas(self):
        lista = (
            list(self.notificacoes_sistema_nao_lidas) +
            list(self.notificacoes_produto_nao_lidas)
        )

        return sorted(
            lista,
            key=lambda x: self._get_data_notificacao(x) or 0,
            reverse=True
        )[:30]

    @cached_property
    def notificacoes_lidas(self):
        lista = (
            list(self.notificacoes_sistema_lidas) +
            list(self.notificacoes_produto_lidas)
        )

        return sorted(
            lista,
            key=lambda x: self._get_data_notificacao(x) or 0,
            reverse=True
        )[:20]

    # ─────────────────────────────────────────────
    # 🌐 CONTEXTO GLOBAL
    # ─────────────────────────────────────────────

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        user = self.request.user

        ctx.update({

            # 👤 IDENTIDADE
            "usuario": user,
            "usuario_nome": user.get_full_name() or user.username,

            # 👥 GRUPOS
            "grupos_usuario": self.grupos_usuario,
            "grupo_principal": self.grupos_usuario[0] if self.grupos_usuario else "Sem grupo",

            # 🏫 PERFIL
            "perfil": self.perfil,
            "escola": getattr(self.perfil, "escola", None),

            # ⚙️ CONFIG
            "config": self.configuracao,
            "itens_por_pagina": self.configuracao.pagina_CardapiosEscolares,

            # 🔔 SISTEMA
            "notificacoes_sistema_nao_lidas": self.notificacoes_sistema_nao_lidas,
            "notificacoes_sistema_lidas": self.notificacoes_sistema_lidas,

            # 🔔 PRODUTO (IMPORTANTE PARA SEU TEMPLATE)
            "notificacoes_produto_nao_lidas": self.notificacoes_produto_nao_lidas,
            "notificacoes_produto_lidas": self.notificacoes_produto_lidas,

            # 🔔 UNIFICADO (fallback / analytics)
            "notificacoes_nao_lidas": self.notificacoes_nao_lidas,
            "notificacoes_lidas": self.notificacoes_lidas,

            # 📊 CONTADOR GLOBAL
            "total_nao_lidas": len(self.notificacoes_nao_lidas),
        })

        return ctx