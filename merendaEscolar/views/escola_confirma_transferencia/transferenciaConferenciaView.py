from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from merendaEscolar.models import Transferencia, DivergenciaEntrega


class TransferenciaConferenciaView(LoginRequiredMixin, DetailView):
    model = Transferencia
    template_name = "merendaEscolar/escola/transferencia_conferencia.html"
    context_object_name = "transferencia"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["itens"] = self.object.itens.all()
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        transferencia = self.get_object()

        # 🔒 Segurança institucional
        if not request.user.is_authenticated:
            raise PermissionDenied("Usuário não autenticado.")

        if transferencia.status != "ENVIADO":
            messages.error(request, "Transferência não está disponível para conferência.")
            return redirect("merendaEscolar:lista_escolas")

        houve_divergencia = False

        for item in transferencia.itens.all():
            qtd_enviada = item.quantidade
            qtd_recebida = float(
                request.POST.get(f"recebido_{item.id}", qtd_enviada)
            )

            descricao = request.POST.get(f"descricao_{item.id}", "").strip()

            if qtd_recebida != qtd_enviada:

                if not descricao:
                    messages.error(
                        request,
                        f"Informe a descrição da divergência para o produto {item.produto.nome}."
                    )
                    return redirect(
                        "merendaEscolar:transferencia-conferencia",
                        pk=transferencia.pk
                    )

                houve_divergencia = True

                DivergenciaEntrega.objects.create(
                    transferencia=transferencia,
                    produto=item.produto,
                    quantidade_enviada=qtd_enviada,
                    quantidade_recebida=qtd_recebida,
                    descricao=descricao,
                    registrado_por=request.user,
                )

        # Atualiza status
        transferencia.status = "RECEBIDO"
        transferencia.data_recebimento = timezone.now()
        transferencia.recebido_por = request.user
        transferencia.save()

        if houve_divergencia:
            messages.warning(request, "Conferência finalizada com divergência registrada.")
        else:
            messages.success(request, "Conferência finalizada com sucesso.")

        return redirect("merendaEscolar:lista_escolas")