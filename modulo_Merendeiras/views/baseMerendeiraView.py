
from core.permissions import GroupRequiredMixin
from core.groups.merenda import MERENDEIRA_GROUPS

class BaseMerendeiraView(GroupRequiredMixin):
    group_required = MERENDEIRA_GROUPS

    def get_escola_usuario(self):

        user = self.request.user
        grupos = user.groups.all()
        perfil = getattr(user, "perfilusuario", None)
        if not perfil:
            return None

        escola = getattr(perfil, "escola", None)
        return escola

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        user = self.request.user
        escola = self.get_escola_usuario()

        grupos = user.groups.all()
        nomes_grupos = [g.name for g in grupos]

        nome_escola = getattr(escola, "nome", None)

        usuario_nome = (
            user.get_full_name()
            or user.username
        )

        # 🔥 CONTEXTO PADRÃO
        ctx["escola_usuario"] = escola
        ctx["nome_escola"] = nome_escola
        ctx["usuario_nome"] = usuario_nome

        # 🔥 NOVO: GRUPOS
        ctx["grupos_usuario"] = nomes_grupos
        ctx["grupo_principal"] = nomes_grupos[0] if nomes_grupos else "Sem grupo"

        return ctx
