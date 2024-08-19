from django.forms import BaseModelForm
from django.views.generic import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin


class EncaminhaEscola (LoginRequiredMixin, CreateView, SuccessMessageMixin):
    def get_form(self, form_class) :
        return super().get_form(form_class)
    pass