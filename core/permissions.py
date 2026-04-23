from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.contrib.auth.mixins import UserPassesTestMixin


class GroupRequiredMixin(UserPassesTestMixin):
    """
    Controle institucional de acesso por grupos.
    Superuser sempre possui acesso.
    """

    group_required: tuple[str, ...] = ()

    def test_func(self):
        user = self.request.user

        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        if not isinstance(self.group_required, (list, tuple)):
            raise ImproperlyConfigured(
                "group_required deve ser uma lista ou tupla de nomes de grupos."
            )

        if not self.group_required:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} deve definir group_required."
            )

        return user.groups.filter(name__in=self.group_required).exists()

    def handle_no_permission(self):
        raise PermissionDenied("Acesso restrito ao perfil autorizado.")
