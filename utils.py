import qrcode
from django.http import HttpResponse
from io import BytesIO
from django.shortcuts import get_object_or_404


def gerar_qrcode_view(request, pk):
    from django.urls import reverse
    from merendaEscolar.models import Transferencia

    transferencia = get_object_or_404(Transferencia, pk=pk)

    url = reverse(
        "modulo_merendeiras:escola_receber_transfe",
        args=[transferencia.pk]
    )

    full_url = request.build_absolute_uri(url)

    qr = qrcode.make(full_url)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    return HttpResponse(buffer.getvalue(), content_type="image/png")