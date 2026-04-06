from django.contrib.auth.mixins import LoginRequiredMixin
from core.permissions import GroupRequiredMixin

MERENDEIRA_GROUPS = (
    "Merendeira",
    "Admin",
)


class MerendeirasRequiredMixin(LoginRequiredMixin, GroupRequiredMixin):
    group_required = MERENDEIRA_GROUPS