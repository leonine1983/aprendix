# views.py
from django.http import JsonResponse
from django.views import View
from django.db.models import Sum
from ...models import EstoqueCentral


class EstoqueCentralAjaxView(View):
    def get(self, request, *args, **kwargs):
        produto_id = request.GET.get("produto_id")

        if not produto_id:
            return JsonResponse({"error": "Produto não informado"}, status=400)

        lotes = (
            EstoqueCentral.objects
            .filter(produto_id=produto_id, quantidade__gt=0)
            .order_by("data_validade")
        )

        total = lotes.aggregate(total=Sum("quantidade"))["total"] or 0

        data = {
            "total": float(total),
            "unidade": lotes.first().produto.unidade_medida.sigla if lotes.exists() else "",
            "lotes": []
        }

        for l in lotes:
            data["lotes"].append({
                "lote": l.lote,
                "quantidade": float(l.quantidade),
                "data_validade": l.data_validade.strftime("%d/%m/%Y") if l.data_validade else None,
                "status_validade": l.status_validade,  # já existe no seu model
            })

        return JsonResponse(data)