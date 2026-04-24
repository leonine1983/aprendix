
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.functional import cached_property

from core.permissions import GroupRequiredMixin
from core.groups.nutricionista import NUTRICIONISTA_GROUPS
from core.models.perfil import PerfilUsuario
from core.models import ConfiguraPessoal
from admin_acessos.models import AtualizacaoNotificacaoSistema


class BaseNutricionistaView(LoginRequiredMixin, GroupRequiredMixin):

    group_required = NUTRICIONISTA_GROUPS
    login_url = "login"

    # ── Dados cacheados por request ──────────────────────────────────────

    @cached_property
    def perfil(self):
        return PerfilUsuario.objects.select_related("escola").filter(
            user=self.request.user
        ).first()

    @cached_property
    def configuracao(self):
        config, _ = ConfiguraPessoal.objects.get_or_create(pk=1)
        return config

    @cached_property
    def grupos_usuario(self):
        return list(self.request.user.groups.values_list("name", flat=True))

    # ✅ CORRETO: cached_property no nível da CLASSE, não dentro de método
    @cached_property
    def notificacoes_nao_lidas(self):
        return AtualizacaoNotificacaoSistema.objects.filter(
            user=self.request.user, lida=False
        ).order_by("-criada_em")[:20]

    @cached_property
    def notificacoes_lidas(self):
        return AtualizacaoNotificacaoSistema.objects.filter(
            user=self.request.user, lida=True
        ).order_by("-criada_em")[:10]

    # ── Contexto global ──────────────────────────────────────────────────

    # ✅ CORRETO: apenas UM get_context_data no nível da classe
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        user = self.request.user
        usuario_nome = user.get_full_name() or user.username
        grupo_principal = self.grupos_usuario[0] if self.grupos_usuario else "Sem grupo"

        ctx.update({
            # Identidade
            "usuario":          user,
            "usuario_nome":     usuario_nome,

            # Grupos
            "grupos_usuario":   self.grupos_usuario,
            "grupo_principal":  grupo_principal,

            # Perfil e escola
            "perfil":           self.perfil,
            "escola":           getattr(self.perfil, "escola", None),

            # Configuração
            "config":           self.configuracao,
            "itens_por_pagina": self.configuracao.pagina_CardapiosEscolares,

            # 🔔 Notificações — agora realmente adicionadas ao contexto
            "notificacoes_nao_lidas": self.notificacoes_nao_lidas,
            "notificacoes_lidas":     self.notificacoes_lidas,
            "total_nao_lidas":        self.notificacoes_nao_lidas.count(),
        })

        return ctx