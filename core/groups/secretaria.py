from django.contrib.auth.mixins import LoginRequiredMixin
from core.permissions import GroupRequiredMixin

SECRETARIOS_GROUPS = (
    "Secretario",
    "Admin",
)

# "Admin", "Professor","Diretor", "Secretario", "Coordenador", "Aluno"

class NutricionistaRequiredMixin(LoginRequiredMixin, GroupRequiredMixin):
    group_required = SECRETARIOS_GROUPS