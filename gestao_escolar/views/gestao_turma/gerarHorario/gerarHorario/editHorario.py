from django.shortcuts import render, get_object_or_404, redirect
from django.forms import modelformset_factory
from django.contrib import messages
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django import forms
from gestao_escolar.models import Turmas, Horario, TurmaDisciplina, Periodo

class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['segunda', 'terca', 'quarta', 'quinta', 'sexta']

class HorarioUpdateView(UpdateView):
    model = Horario
    form_class = HorarioForm
    template_name = 'Escola/inicio.html'

    def get_object(self, queryset=None):
        horario_id = self.kwargs['pk']
        turma_id = self.kwargs['turma_id']
        return get_object_or_404(Horario, id=horario_id, turma_id=turma_id)
    
    def get_success_url(self):
        return reverse_lazy('Gestao_Escolar:edit_horario', kwargs={'turma_id': self.kwargs['turma_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context.update({
            'horarios': Horario.objects.filter(turma=self.kwargs['turma_id']),
            'periodos': Periodo.objects.all(),
            'conteudo_page': "Gestão Turmas - GerarHorario"
        })
        return context

    def form_valid(self, form):
        horario = form.instance
        turma_id = self.kwargs['turma_id']
        periodo = horario.periodo

        dias_semana = ['segunda', 'terca', 'quarta', 'quinta', 'sexta']
        errors = []
        """"""
        # Verificação de duplicação no mesmo período para diferentes turmas
        for dia in dias_semana:
            turma_disciplina = getattr(horario, dia)
            if turma_disciplina:
                # Verifica se a mesma instância de TurmaDisciplina está sendo usada no mesmo período em outra turma
                if Horario.objects.filter(
                    **{dia: turma_disciplina},
                    periodo=periodo
                ).exclude(turma=horario.turma).exists():
                    outra_turma = Horario.objects.filter(
                        **{dia: turma_disciplina},
                        periodo=periodo
                    ).exclude(turma=horario.turma).first().turma
                    errors.append(
                        f'A instância {turma_disciplina} já está vinculada na turma {outra_turma} para este mesmo período em {dia}.'
                    )

        # Verificação de limites de aulas por dia e por semana
        for dia in dias_semana:
            turma_disciplina = getattr(horario, dia)
            if turma_disciplina:
                # Verificação do limite diário
                total_aulas_dia = Horario.objects.filter(
                    **{dia: turma_disciplina},
                    turma=horario.turma
                ).count()
                if total_aulas_dia >= turma_disciplina.quant_aulas_dia:
                    errors.append(
                        f'O limite diário de {turma_disciplina.quant_aulas_dia}\
                              aulas para {turma_disciplina.disciplina.nome.upper()}\
                                  com o professor {turma_disciplina.professor.nome.encaminhamento.contratado.nome.upper()}\
                                      em {dia} foi atingido. Se precisar acrescentar mais aulas para esse professor, \
                                        vá em GRADES DE DISCIPLINAS e aumente a quantidade de "Aulas Dia" dessa disciplina com esse professor.'
                    )

                # Verificação do limite semanal
                total_aulas_semana = sum(
                    Horario.objects.filter(
                        **{d: turma_disciplina},
                        turma=horario.turma
                    ).count() for d in dias_semana
                )
                if total_aulas_semana >= turma_disciplina.quant_aulas_semana:
                    errors.append(
                        f'O limite semanal de {turma_disciplina.quant_aulas_semana} aulas para {turma_disciplina.disciplina.nome.upper()}\
                              com o professor {turma_disciplina.professor.nome.encaminhamento.contratado.nome.upper()} foi atingido.\
                                Se precisar acrescentar mais aulas para esse professor, \
                                        vá em GRADES DE DISCIPLINAS e aumente a quantidade de "Aulas por Semana" dessa disciplina com esse professor.'
                    )                

        # Se houver erros, adiciona as mensagens de erro e retorna o formulário inválido
        if errors:
            for error in errors:
                messages.error(self.request, error)
            return self.form_invalid(form)
        
        # Se não houver erros, processa o formulário normalmente
        messages.success(self.request, '✅ Período de aula atualizado com sucesso!')
        return super().form_valid(form)
