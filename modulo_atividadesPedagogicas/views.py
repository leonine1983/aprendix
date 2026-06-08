from django.shortcuts import render

def atividadePedagogicaView(request):
    return render (request, "atividadesPedagogicas/atividadesPedagogicas.html")

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .models import JogoPedagogico
from django import forms


class JogoPedagogicoForm(forms.ModelForm):

    class Meta:
        model = JogoPedagogico

        fields = [
            "titulo",
            "resumo",
            "descricao",
            "objetivo_pedagogico",
            "imagem_capa",
            "icone",
            "link_externo",
            "modalidade",
            "dificuldade",
            "tempo_estimado",
            "quantidade_jogadores",
            "destaque",
            "publicado",
            "graus_escolares",
            "series",
            "disciplinas",
            "habilidades_bncc",
            "categorias",
            "tags",
        ]

        widgets = {

            "titulo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: Corrida Matemática"
                }
            ),

            "resumo": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            ),

            "modalidade": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "dificuldade": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "tempo_estimado": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

        }

class JogoPedagogicoCreateView(CreateView):

    model = JogoPedagogico

    form_class = JogoPedagogicoForm

    template_name = "atividadesPedagogicas/pages/jogo_form.html"

    success_url = reverse_lazy(
        "atividadePedagogica:jogo_create"
    )


    def form_valid(self, form):

        response = super().form_valid(form)

        messages.success(
            self.request,
            f'Jogo "{self.object.titulo}" cadastrado com sucesso.'
        )

        return response

    def form_invalid(self, form):

        messages.error(
            self.request,
            "Existem erros no formulário. Verifique os campos destacados."
        )

        return super().form_invalid(form)



