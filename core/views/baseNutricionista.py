from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property

from core.permissions import GroupRequiredMixin
from core.groups.nutricionista import NUTRICIONISTA_GROUPS
from core.models.perfil import PerfilUsuario
from core.models import ConfiguraPessoal


class BaseNutricionistaView(LoginRequiredMixin, GroupRequiredMixin):
    """
    🔷 Base institucional para Nutricionistas

    Responsabilidades:
    ✔ Autenticação obrigatória
    ✔ Autorização por grupo institucional
    ✔ Carregamento de contexto global (perfil, config, escola)
    ✔ Redução de queries repetidas (cached_property)
    ✔ Padronização de UX entre templates

    Basta herdar — NÃO precisa usar LoginRequiredMixin nem repetir lógica.
    """

    group_required = NUTRICIONISTA_GROUPS
    login_url = "login"  # ajuste conforme seu projeto

    # ==============================
    # 🔷 CAMADA DE DADOS (CACHE)
    # ==============================

    @cached_property
    def perfil(self):
        """
        Retorna o perfil do usuário logado.
        Evita múltiplas queries na mesma request.
        """
        return PerfilUsuario.objects.select_related("escola").filter(user=self.request.user).first()

    @cached_property
    def configuracao(self):
        """
        Configuração global do sistema.
        Usa get_or_create para garantir existência.
        """
        config, _ = ConfiguraPessoal.objects.get_or_create(pk=1)
        return config

    @cached_property
    def grupos_usuario(self):
        return list(self.request.user.groups.values_list("name", flat=True))

    # ==============================
    # 🔷 CONTEXTO GLOBAL
    # ==============================

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        user = self.request.user

        # 🔷 Nome institucional
        usuario_nome = user.get_full_name() or user.username

        # 🔷 Grupo principal (primeiro)
        grupo_principal = (
            self.grupos_usuario[0]
            if self.grupos_usuario else "Sem grupo"
        )

        # ==============================
        # 🔷 CONTEXTO PADRÃO INSTITUCIONAL
        # ==============================

        ctx.update({
            # 👤 Identidade
            "usuario": user,
            "usuario_nome": usuario_nome,

            # 👥 Grupos
            "grupos_usuario": self.grupos_usuario,
            "grupo_principal": grupo_principal,

            # 🧾 Perfil completo
            "perfil": self.perfil,

            # 🏫 Escola vinculada (atalho importante)
            "escola": getattr(self.perfil, "escola", None),

            # ⚙️ Configuração do sistema
            "config": self.configuracao,

            # 🔢 Config específica (atalho UX)
            "itens_por_pagina": self.configuracao.pagina_CardapiosEscolares,
        })

        return ctx