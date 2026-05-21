from django.views.generic import ListView
from django.contrib import messages

from merendaEscolar.models import Transferencia
from core.permissions import GroupRequiredMixin
from core.groups.merenda import MERENDEIRA_GROUPS
from .baseMerendeiraView import BaseMerendeiraView

  


from django.contrib.auth.mixins import LoginRequiredMixin
"""
class TransferenciasAbertasListView(LoginRequiredMixin, BaseMerendeiraView, ListView):
   
    Exibe todas as transferências enviadas e ainda não recebidas de uma escola.
 
    model = Transferencia
    context_object_name = "transferencias"
    template_name = "modulo_merendeiras/transferencia/conferir_transferencia.html"
    group_required = MERENDEIRA_GROUPS

    def get_queryset(self):
        escola_id = self.get_escola_usuario()
        return Transferencia.objects.filter(
            escola_destino_id=escola_id,
            status="ENVIADO"
        ).order_by("-criado_em")

    """
from django.views.generic import ListView
from django.contrib import messages
from django.db.models import Q
from django.utils.timezone import now

from merendaEscolar.models import Transferencia
from core.groups.merenda import MERENDEIRA_GROUPS
from core.views.baseMerendeira import BaseMerendeiraView


class TransferenciasEscolaListView(BaseMerendeiraView, ListView):
    template_name = "modulo_merendeiras/transferencia/conferir_transferencia.html"
    context_object_name = "pendentes"
    group_required = MERENDEIRA_GROUPS

    def get_queryset(self):
        escola = self.get_escola_usuario()

        if not escola:
            messages.error(self.request, "Usuário sem vínculo com escola.")
            return Transferencia.objects.none()

        queryset = (
            Transferencia.objects
            .filter(
                escola_destino=escola,
                status__in=["ENVIADO", "EM_CONFERENCIA"]
            )
            .order_by("-criado_em")
        )

        if not queryset.exists():
            messages.info(self.request, "Nenhuma transferência pendente.")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        escola = self.get_escola_usuario()
        request = self.request

        # 🔍 Filtros
        numero = request.GET.get("numero")
        ano = request.GET.get("ano")
        semana = request.GET.get("semana")

        

        confirmadas = Transferencia.objects.filter(
            escola_destino=escola,
            status="RECEBIDO"          
        )
        print(f'todos as transfrencia: {confirmadas}')
        #

        # 🎯 Aplicação dos filtros
        if numero:
            confirmadas = confirmadas.filter(numero__icontains=numero)

        if ano:
            confirmadas = confirmadas.filter(criado_em__year=ano)

        if semana:
            confirmadas = confirmadas.filter(criado_em__week=semana)

        confirmadas = confirmadas.order_by("-criado_em")

        # Feedback institucional
        if numero or ano or semana:
            messages.info(self.request, "Filtros aplicados na busca de transferências confirmadas.")

        context["confirmadas"] = confirmadas
        context["filtros"] = {
            "numero": numero or "",
            "ano": ano or "",
            "semana": semana or "",
        }

        return context