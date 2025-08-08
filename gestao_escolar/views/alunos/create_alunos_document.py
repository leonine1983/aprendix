from datetime import datetime

from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

from gestao_escolar.models import Alunos, Bairro
from .partials_alunos.alunos_form import Aluno_documento_form


class Create_Alunos_Document(UpdateView, SuccessMessageMixin ):
    model = Alunos
    form_class = Aluno_documento_form
    template_name = 'Escola/inicio.html'
    success_message = "Aluno registrado com sucesso!!"

    def get_success_url(self):
        return reverse_lazy(
            'Gestao_Escolar:alunos_perfil', 
            kwargs={'pk': self.kwargs['pk']}
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['aluno_create'] = Alunos.objects.filter(pk=self.kwargs['pk'])
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        # Sempre definir um valor no login_aluno
        if not self.object.login_aluno:
            initial['login_aluno'] = self.form_class.generate_login(self)
        else:
            initial['login_aluno'] = self.object.login_aluno
        return initial  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'titulo_page': 'Alunos',
            'bairros': Bairro.objects.all(),
            'Alunos': Alunos.objects.all(),
            'now': datetime.now(),
            'conteudo_page': 'Registrar Alunos Documento',
            'page_ajuda': (
                "<div class='m-2'>"
                "<b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."
            )
        })

        return context
