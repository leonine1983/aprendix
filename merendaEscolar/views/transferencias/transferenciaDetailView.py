from django.views.generic import DetailView
from ...models import Transferencia
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from core.views.baseNutricionista import BaseNutricionistaView

class TransferenciaDetailView(BaseNutricionistaView, DetailView):
    model = Transferencia
    template_name = "merendaEscolar/transferencia/transferencia_detail.html"
    context_object_name = "transferencia"
    