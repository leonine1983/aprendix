from django.contrib.auth.mixins import LoginRequiredMixin
from core.permissions import GroupRequiredMixin

NUTRICIONISTA_GROUPS = (
    "Nutricionista",
    "Admin",
)

class NutricionistaRequiredMixin(LoginRequiredMixin, GroupRequiredMixin):
    group_required = NUTRICIONISTA_GROUPS