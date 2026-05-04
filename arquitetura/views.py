import subprocess
import sys
from pathlib import Path

from django.views.generic import TemplateView
from django.contrib import messages
from django.shortcuts import redirect
from django.conf import settings

from core.views.baseNutricionista import BaseNutricionistaView
import shutil
import subprocess
import sys
from pathlib import Path

from django.contrib import messages
from django.shortcuts import redirect
from django.conf import settings
from django.views.generic import TemplateView

from core.permissions import GroupRequiredMixin
from core.groups.merenda import MERENDEIRA_GROUPS
from core.views.baseNutricionista import BaseNutricionistaView


class Grafo3DView(GroupRequiredMixin, TemplateView):
    template_name = "arquitetura/grafo_3d.html"
    group_required = MERENDEIRA_GROUPS

    def get(self, request, *args, **kwargs):
        messages.info(request, "Visualização arquitetural do sistema carregada.")
        return super().get(request, *args, **kwargs)


class AtualizarGrafoView(BaseNutricionistaView, TemplateView):

    def get(self, request, *args, **kwargs):
        try:
            static_path = Path(settings.BASE_DIR) / "static" / "arquitetura" / "grafo.json"
            media_path = Path(settings.BASE_DIR) / "media" / "arquitetura" / "grafo.json"

            static_path.parent.mkdir(parents=True, exist_ok=True)
            media_path.parent.mkdir(parents=True, exist_ok=True)

            result = subprocess.run(
                [
                    sys.executable,
                    "manage.py",
                    "graph_models",
                    "-a",
                    "--json",
                    "-o",
                    str(static_path),
                ],
                check=True,
                capture_output=True,
                text=True,
                cwd=settings.BASE_DIR,  # garante execução na raiz do projeto
            )

            shutil.copy(static_path, media_path)

            messages.success(request, "Grafo atualizado com sucesso.")

        except subprocess.CalledProcessError as e:
            messages.error(request, f"Erro ao gerar grafo: {e.stderr}")

        except Exception as e:
            messages.error(request, f"Erro inesperado: {str(e)}")

        return redirect("arquitetura_system:grafo_3d")