from ..models import PerfilUsuario
from django.views.generic import DetailView
from django.core.exceptions import PermissionDenied


class CurriculoPublicoView(DetailView):
    model = PerfilUsuario
    template_name = "core/conta/curriculo_publico.html"
    context_object_name = "perfil"
    slug_field = "slug_publico"
    slug_url_kwarg = "slug"

    def get_object(self):
        perfil = super().get_object()

        if perfil.visibilidade_curriculo == "privado":
            raise PermissionDenied

        if (
            perfil.visibilidade_curriculo == "restrito"
            and not self.request.user.is_authenticated
        ):
            raise PermissionDenied

        return perfil