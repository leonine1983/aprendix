from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

from gestao_escolar.models import Alunos
from .partials_alunos.alunos_form import Alunos_form


class Create_Alunos(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Alunos
    form_class = Alunos_form
    template_name = 'Escola/inicio.html'
    success_message = "Aluno registrado com sucesso!!"
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')

    def get_success_url(self):
        return reverse_lazy('Gestao_Escolar:alunos_create_etapa2', kwargs={'pk': self.object.id})

    def get_queryset(self):
        busca_nome = self.request.GET.get('busca-aluno', '').strip()
        if busca_nome:
            return Alunos.objects.filter(nome_completo__icontains=busca_nome)
        return Alunos.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'titulo_page': 'ALUNOS – Relação de todos os estudantes registrados na plataforma Aprendix.',
            'conteudo_page': 'Registrar Alunos',
            'sub_Info_page': (
                'Antes de procedermos com o cadastro do aluno, é imprescindível realizar uma verificação '
                'para confirmar se ele já está registrado no sistema. Essa medida visa evitar duplicatas e '
                'garantir a integridade dos dados.'
            ),
            'mascara_cpf': True,
            'Alunos': self.get_queryset(),
            'now': timezone.now(),
            'bottom': 'Avançar',
            'page_ajuda': "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional.",
        })
        return context

    def form_valid(self, form):
        nome_completo = form.cleaned_data.get('nome_completo', '').strip()
        nome_mae = form.cleaned_data.get('nome_mae', '').strip()

        if Alunos.objects.filter(
            nome_completo__icontains=nome_completo,
            nome_mae__icontains=nome_mae
        ).exists():
            return redirect(
                'Gestao_Escolar:alunos_encontred',
                nome_completo=nome_completo,
                nome_mae=nome_mae
            )

        user = self.request.user
        nome_usuario = f'{user.first_name} {user.last_name}'.strip() or user.username
        form.instance.res_cadastro = nome_usuario
        form.instance.nome_completo = nome_completo.upper()
        form.instance.nome_mae = nome_mae.upper()

        return super().form_valid(form)

    def form_invalid(self, form):
        for field_errors in form.errors.values():
            for error in field_errors:
                messages.error(self.request, error)
        return super().form_invalid(form)
