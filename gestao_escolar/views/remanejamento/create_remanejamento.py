from gestao_escolar.models import Matriculas, Turmas, Remanejamento
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from .remanejamento_form import Matricula_form




from django.contrib import messages
from django.utils import timezone

class Create_Remanejamento(LoginRequiredMixin, CreateView):
    model = Remanejamento
    fields = '__all__'
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')
    success_message = "Aluno remanejado com sucesso!"

from django.contrib import messages
from django.utils import timezone
from django import forms

class RemanejamentoForm(forms.ModelForm):
    class Meta:
        model = Remanejamento
        fields = ['tipo', 'aluno', 'turma_nova', 'description']

    def __init__(self, *args, **kwargs):
        matricula_id = kwargs.pop('matricula_id', None)
        super().__init__(*args, **kwargs)

        if matricula_id:
            self.fields['aluno'].queryset = Matriculas.objects.filter(pk=matricula_id)
            self.fields['aluno'].initial = matricula_id


class Create_Remanejamento(LoginRequiredMixin, CreateView):
    model = Remanejamento
    form_class = RemanejamentoForm
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['matricula_id'] = self.kwargs['pk']
        return kwargs

    def form_valid(self, form):
        remanejamento = form.save(commit=False)
        remanejamento.profissional_q_remanejou = self.request.user

        matricula = remanejamento.aluno
        tipo = remanejamento.tipo.nome

        # MUDANÇA DE TURMA
        if tipo == 'Mudança de Turma':
            # Guarda a turma anterior
            remanejamento.turma_anterior = matricula.turma

            # Atualiza matrícula
            matricula.turma = remanejamento.turma_nova
            matricula.remanejado = True
            matricula.desistente = False
            matricula.transferido = False
            matricula.situacao_na_turma = f'Remanejado do {remanejamento.turma_anterior}'
            matricula.save()

            remanejamento.save()

            messages.success(
                self.request,
                "Aluno remanejado para nova turma com sucesso."
            )

            return super().form_valid(form)

        # Continua fluxo normal para outros tipos
        remanejamento.save()
        return super().form_valid(form)



    def get_context_data(self, **kwargs):
        svg = '<i class="fa-sharp fa-regular fa-layer-plus"></i>'
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Remanejamento'          
        context['svg'] = svg 
        context['pk_aluno'] = self.kwargs['pk']
        context['info_matrilula'] = Matriculas.objects.filter(pk = self.kwargs['pk']) 
        context['conteudo_page'] = "Remaneja Aluno"  
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."        
        return context
            







            