from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from core.permissions import GroupRequiredMixin
from core.groups.nutricionista import NUTRICIONISTA_GROUPS
from ...models import Transferencia


from django.urls import reverse
from django.utils.http import urlencode

import qrcode
import base64
from io import BytesIO
from core.views.baseNutricionista import BaseNutricionistaView

class TransferenciaPrintView(BaseNutricionistaView, DetailView):
    model = Transferencia
    template_name = "merendaEscolar/transferencia/transferencia_print.html"
    context_object_name = "transferencia"

    group_required = NUTRICIONISTA_GROUPS
    permission_required = "merendaEscolar.view_transferencia"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transferencia = self.object

        # 🔗 URL ABSOLUTA de recebimento
        url = self.request.build_absolute_uri(
            reverse("modulo_merendeiras:escola_receber_transfe", args=[transferencia.pk])
        )

        # 🧠 Geração do QRCode
        qr = qrcode.make(url)

        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        context["qr_code"] = qr_base64
        context["url_recebimento"] = url  # opcional (auditoria)

        return context