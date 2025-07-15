from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView,
    CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from rh.models import Prefeitura


class PrefeituraListView(ListView):
    model = Prefeitura
    template_name = "prefeitura/prefeitura_list.html"
    context_object_name = "prefeituras"
    paginate_by = 10


class PrefeituraDetailView(DetailView):
    model = Prefeitura
    template_name = "prefeitura/prefeitura_detail.html"
    context_object_name = "prefeitura"


class PrefeituraCreateView(CreateView):
    model = Prefeitura
    fields = (
        "nome", "instituto", "cidade", "estado",
        "endereco", "pessoa_publica", "brasao"
    )
    template_name = "prefeitura/prefeitura_form.html"
    success_url = reverse_lazy("prefeitura:lista")



from django import forms

from django import forms


class PrefeituraForm(forms.ModelForm):
    class Meta:
        model = Prefeitura
        # use apenas os campos que quer expor no formulário
        fields = [
            "nome",
            "instituto",
            "cidade",
            "estado",
            "endereco",
            "pessoa_publica",
            "brasao",
        ]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "instituto": forms.TextInput(attrs={"class": "form-control"}),
            "cidade": forms.Select(attrs={"class": "form-select"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "endereco": forms.TextInput(attrs={"class": "form-control"}),
            "pessoa_publica": forms.TextInput(attrs={"class": "form-control"}),
            # input oculto para o drag‑and‑drop
            "brasao": forms.ClearableFileInput(
                attrs={"class": "d-none", "id": "id_brasao_input"}
            ),
        }


class PrefeituraUpdateView(LoginRequiredMixin, UpdateView):
    model = Prefeitura
    form_class = PrefeituraForm
    template_name = "Escola/inicio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['conteudo_page'] = 'prefeituraUdate' 
        return context
    
    def get_success_url(self):
        pref = self.request.session['escola_nome_query']
        messages.success(self.request, "Prefeitura Atualizada com sucesso!")
        return reverse_lazy("Gestao_Escolar:PrefeituraEditar", kwargs={'pk':pref.prefeitura.id})



class PrefeituraDeleteView(DeleteView):
    model = Prefeitura
    template_name = "prefeitura/prefeitura_confirm_delete.html"
    success_url = reverse_lazy("prefeitura:lista")
