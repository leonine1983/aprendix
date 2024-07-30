"""from django import forms
from django.views import View
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from gestao_escolar.models import Horario, Turmas, Periodo, Validade_horario
from .forms import HorarioForm

class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'validade']   

    def __init__(self, *args, **kwargs):
        validade_ativa = kwargs.pop('validade_ativa', None)
        super().__init__(*args, **kwargs)
        if validade_ativa:
            self.fields['validade'].required = False
            self.fields['validade'].initial = validade_ativa
            self.fields['validade'].widget = forms.HiddenInput()  # Esconder o campo no formulário, se necessário


class HorarioCreateView(View):
    template_name = 'Escola/inicio.html'

    def get(self, request, *args, **kwargs):
        turma_id = self.kwargs['turma_id']
        turma = get_object_or_404(Turmas, pk=turma_id)
        periodos = Periodo.objects.all()
        validade_ativa = Validade_horario.objects.filter(horario_ativo=True).first()

        forms_periodos = [(HorarioForm(initial={'turma': turma, 'periodo': periodo}, prefix=str(periodo.id), validade_ativa=validade_ativa), periodo) for periodo in periodos]
        context = {
            'forms_periodos': forms_periodos,
            'turma': turma,
            'conteudo_page': "Gestão Turmas - GerarHorario",
            'horarios': Horario.objects.filter(turma=turma)
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        turma_id = self.kwargs['turma_id']
        turma = get_object_or_404(Turmas, pk=turma_id)
        periodos = Periodo.objects.all()
        validade_ativa = Validade_horario.objects.filter(horario_ativo=True).first()
        
        forms = [HorarioForm(request.POST, prefix=str(periodo.id), validade_ativa=validade_ativa) for periodo in periodos]

        if all(form.is_valid() for form in forms):
            for form in forms:
                periodo_id = request.POST.get(f'{form.prefix}-periodo')
                periodo = get_object_or_404(Periodo, pk=periodo_id)
                horario_instance = form.save(commit=False)
                horario_instance.turma = turma
                horario_instance.periodo = periodo
                horario_instance.validade = validade_ativa
                horario_instance.save()
            messages.success(request, 'Horários atualizados com sucesso.')
            return HttpResponseRedirect(self.get_success_url())
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
            forms_periodos = [(form, Periodo.objects.get(pk=form.prefix).nome_periodo) for form in forms]
            context = {
                'forms_periodos': forms_periodos,
                'turma': turma,
                'conteudo_page': "Gestão Turmas - GerarHorario",
                'horarios': Horario.objects.filter(turma=turma)
            }
            return render(request, self.template_name, context)

    def get_success_url(self):
        return reverse_lazy('Gestao_Escolar:criar_horario', kwargs={'turma_id': self.kwargs['turma_id']})
    
    """
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.forms import modelform_factory
from django.contrib import messages
from rh.models import Escola
from gestao_escolar.models import Turmas, Horario, Periodo, Validade_horario
from django.urls import reverse
from django.utils import timezone

def alocar_aulas(request, turma_id):
    turma = get_object_or_404(Turmas, id=turma_id)    
    gradeHorario = Horario.objects.filter(turma=turma_id)    
    gradePeriodo = Periodo.objects.filter(turma = turma_id) 

    if not gradePeriodo.exists():            
                    sessao = request.session['escola_id']
                    Periodo.objects.create(
                        escola = Escola.objects.get(id = sessao),
                        turma = Turmas.objects.get(id = turma_id),
                        nome_periodo="1º Periodo",
                        hora_inicio=timezone.datetime.strptime('08:00', '%H:%M').time(),
                        hora_fim=timezone.datetime.strptime('08:45', '%H:%M').time()
                    )
                    Periodo.objects.create(
                        escola = Escola.objects.get(id = sessao),
                        turma = Turmas.objects.get(id = turma_id),
                        nome_periodo="2º Período",
                        hora_inicio=timezone.datetime.strptime('08:45', '%H:%M').time(),
                        hora_fim=timezone.datetime.strptime('09:50', '%H:%M').time()
                    )
                    
                    Periodo.objects.create(
                        escola = Escola.objects.get(id = sessao),
                        turma = Turmas.objects.get(id = turma_id),
                        nome_periodo="3º Período",
                        hora_inicio=timezone.datetime.strptime('09:50', '%H:%M').time(),
                        hora_fim=timezone.datetime.strptime('10:15', '%H:%M').time()
                    )
                    Periodo.objects.create(
                        escola = Escola.objects.get(id = sessao),
                        turma = Turmas.objects.get(id = turma_id),
                        nome_periodo="4º Período",
                        hora_inicio=timezone.datetime.strptime('10:30', '%H:%M').time(),
                        hora_fim=timezone.datetime.strptime('11:15', '%H:%M').time()
                    )
                    
                    Periodo.objects.create(
                        escola = Escola.objects.get(id = sessao),
                        turma = Turmas.objects.get(id = turma_id),
                        nome_periodo="5º Período",
                        hora_inicio=timezone.datetime.strptime('11:15', '%H:%M').time(),
                        hora_fim=timezone.datetime.strptime('12:00', '%H:%M').time()
                    )      
    
    for gP in gradePeriodo:
        if Validade_horario.objects.exists():
            if not gradeHorario.filter(periodo = gP.id):  
                    valida = Validade_horario.objects.get(horario_ativo = True).id             
                    Horario.objects.update_or_create(
                            validade = Validade_horario.objects.get(id = valida ),
                            periodo = Periodo.objects.get(id = gP.id), 
                            turma = turma,
                            )
        else:
                messages.error(request, "🔔 Você ainda não criou o período de vigência.")
                return redirect(reverse('Gestao_Escolar:validadeHorario', kwargs={'turma_id': turma_id}))

    return redirect(reverse('Gestao_Escolar:edit_horario', kwargs={'turma_id': turma_id}))






   