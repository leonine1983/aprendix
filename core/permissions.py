from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class GroupRequiredMixin(UserPassesTestMixin):
    """
    Controle institucional de acesso por grupos.
    Superuser sempre possui acesso.
    """

    group_required = []

    def test_func(self):
        user = self.request.user

        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return user.groups.filter(name__in=self.group_required).exists()

    def handle_no_permission(self):
        raise PermissionDenied("Acesso restrito ao perfil autorizado.")
