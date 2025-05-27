from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.http import  HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView
from django import forms
from django.db.models import Q

from gestao_escolar.models import (
    Turmas, TurmaDisciplina, Trimestre,
    Matriculas, Presenca
)
from rh.models import  Encaminhamentos, UserPessoas
from modulo_professor.models import (
    ComposicaoNotas, AulaDada, AnexoAula, PlanoDeAula
)

from collections import defaultdict
from datetime import datetime, date



class ComposicaoNotasForm(forms.ModelForm):
    class Meta:
        model = ComposicaoNotas
        fields = [ 'prova', 'trabalho', 'participacao', 'tarefas', 'anotacoes', 'prova_paralela']
        widgets = {
            'anotacoes': forms.Textarea(attrs={'rows': 3}),
        }


@login_required
def criaNotasComposicao(request, aluno, grade, trimestre):
    aluno_obj = get_object_or_404(Matriculas, id=aluno)
    grade_obj = get_object_or_404(TurmaDisciplina, id=grade)
    trimestre_obj = get_object_or_404(Trimestre, id=trimestre)

    composicao_existente = ComposicaoNotas.objects.filter(
        aluno=aluno_obj,
        grade=grade_obj,
        trimestre=trimestre_obj
    ).first()

    if request.method == "POST":
        form = ComposicaoNotasForm(request.POST, instance=composicao_existente)
        if form.is_valid():
            confirmar = request.POST.get("confirmar", "nao")

            if composicao_existente and confirmar != "sim":
                return render(request, "modulo_professor/partial/notas/confirmaAtualiza.html", {
                    "form": form,
                    "confirmar_pendente": True,
                })

            nova_instancia = form.save(commit=False)
            nova_instancia.aluno = aluno_obj
            nova_instancia.grade = grade_obj
            nova_instancia.trimestre = trimestre_obj
            nova_instancia.save()

            messages.success(request, "Notas do aluno foram salvas com sucesso!")

            # Recupera os valores simulando um GET
            trimestre_valor = trimestre_obj.id
            disciplina_valor = grade_obj.id 
            # Monta a URL com parâmetros GET
            url = reverse("modulo_professor:homeProfessor")
            query_string = f"?trimestre={trimestre_valor}&disciplina={disciplina_valor}"
            full_url = f"{url}{query_string}"
            return HttpResponseRedirect(full_url)

    else:
        form = ComposicaoNotasForm(instance=composicao_existente)

    return render(request, "modulo_professor/partial/notas/notas.html", {
        "form": form,
        'grade': grade_obj,
        'aluno': aluno_obj
    })


class ComposicaoRecuperaForm(forms.ModelForm):
    class Meta:
        model = ComposicaoNotas
        fields = ['recuperacao_final']  # adicione outros campos se quiser exibir mais


def atualizaRecuperaFinal(request, pk, grade):
    # Obtém o trimestre final
    try:
        tFinal = Trimestre.objects.get(final=True)
    except Trimestre.DoesNotExist:
        messages.error(request, "Trimestre final não está configurado.")
        return redirect('sua_view_de_erro')  # Redirecione apropriadamente

    # Obtém ou cria ComposicaoNotas para esse aluno/grade no trimestre final
    aluno = get_object_or_404(Matriculas, pk=pk)
    grade_disc = get_object_or_404(TurmaDisciplina, pk=grade)

    comp, created = ComposicaoNotas.objects.get_or_create(
        aluno=aluno,
        grade=grade_disc,
        trimestre=tFinal
    )

    if request.method == 'POST':
        form = ComposicaoRecuperaForm(request.POST, instance=comp)
        if form.is_valid():
            form.save()
            messages.success(request, f"Recuperação final atualizada com sucesso. Aluno {aluno}")
            return redirect('modulo_professor:homeProfessor')  # Redirecione após salvar
        else:
            messages.error(request, "Erro ao salvar os dados. Verifique o formulário.")
    else:
        form = ComposicaoRecuperaForm(instance=comp)

    context = {
        'form': form,
        'aluno': aluno,
        'grade': grade_disc,
        'composicao': comp,
        'criado': created
    }

    return render(request, 'modulo_professor/partial/recuperação/recuperaFinal.html', context)



# PRESENÇA ------------------------------------------------------------------
# PRESENÇA DIÁRIA ------------------------
@login_required
def registrar_presenca_diaria_view(request, turma_id):
    turma = get_object_or_404(Turmas, id=turma_id)
    matriculas = Matriculas.objects.filter(turma=turma)

    if request.method == 'POST':
        data_presenca_str = request.POST.get('data')
        try:
            data_presenca = datetime.strptime(data_presenca_str, '%Y-%m-%d').date()
        except ValueError:
            return render(request, 'modulo_professor/partial/presenca/presenca_diaria.html', {
                'matriculas': matriculas,
                'turma': turma,
                'today': date.today(),
                'erro': 'Data inválida. Use o formato yyyy-mm-dd.'
            })

        alunos_presentes_ids = request.POST.getlist('presentes')
        for matricula in matriculas:
            presente = str(matricula.id) in alunos_presentes_ids
            Presenca.objects.update_or_create(
                matricula=matricula,
                data=data_presenca,
                turma_disciplina=None,
                aula_numero=None,
                defaults={'presente': presente, 'controle_diario': True}
            )
        return redirect('modulo_professor:lista_presenca_diaria', turma.id, data_presenca.strftime('%Y-%m-%d'))


    return render(request, 'modulo_professor/partial/presenca/presenca_diaria.html', {
        'matriculas': matriculas,
        'turma': turma,
        'today': date.today()
    })


@login_required
def lista_presenca_diaria_view(request, turma_id, data_str):
    turma = get_object_or_404(Turmas, id=turma_id)
    data_presenca = datetime.strptime(data_str, '%Y-%m-%d').date()
    
    presencas = Presenca.objects.filter(turma_disciplina=None, controle_diario=True, data=data_presenca, matricula__turma=turma)

    alunos_presentes = presencas.filter(presente=True)
    alunos_faltosos = presencas.filter(presente=False)

    return render(request, 'modulo_professor/partial/presenca/lista_presenca_diaria.html', {
        'turma': turma,
        'data': data_presenca,
        'presentes': alunos_presentes,
        'faltosos': alunos_faltosos,
    })


# ------- Mostra faltas -------------------------
@login_required
def historico_faltas_view(request, matricula_id):
    matricula = get_object_or_404(Matriculas, id=matricula_id)
    presencas = Presenca.objects.filter(matricula=matricula).order_by('data')

    faltas_por_mes = defaultdict(lambda: [None]*31)  # 31 dias no máximo

    for presenca in presencas:
        if not presenca.presente:
            mes = presenca.data.month
            dia = presenca.data.day
            faltas_por_mes[mes][dia - 1] = 'F'  # 'F' para Falta

    # Gerando intervalo de dias para passar ao template
    dias_do_mes = list(range(1, 32))  # Dias de 1 a 31

    return render(request, 'modulo_professor/partial/presenca/historico_faltasDias.html', {
        'matricula': matricula,
        'faltas_por_mes': dict(faltas_por_mes),
        'dias_do_mes': dias_do_mes,
    })



# PRESENÇA POR AULA
@login_required
def selecionaTurma(request):
    userProfessor = request.user.related_vinculoUserPessoa
    pessoa = userProfessor.pessoa.id  
    professorGrade = TurmaDisciplina.objects.filter(professor__encaminhamento__contratado__id=pessoa)
    return render(request, 'modulo_professor/partial/presenca/selecionaTurma.html', {'pessoa':professorGrade})


# PRESENÇA POR DISCIPLINA
@login_required
def selecionaTurmaDisciplina(request):
    userProfessor = request.user.related_vinculoUserPessoa
    pessoa = userProfessor.pessoa.id  
    professorGrade = TurmaDisciplina.objects.filter(professor__encaminhamento__contratado__id=pessoa)
    return render(request, 'modulo_professor/partial/presenca/selecionaTurmaDisciplina.html', {'pessoa':professorGrade})



@login_required
def registrar_presenca_por_aula_view(request, turma_disciplina_id):
    turma_disciplina = get_object_or_404(TurmaDisciplina, id=turma_disciplina_id)
    turma = turma_disciplina.turma
    matriculas = Matriculas.objects.filter(turma=turma)

    if request.method == 'POST':
        data_presenca_str = request.POST.get('data')
        aula_numero = request.POST.get('aula_numero')
        alunos_presentes_ids = request.POST.getlist('presentes')
        data_presenca = data_presenca_str

        # Registro das presenças por aula
        for matricula in matriculas:
            presente = str(matricula.id) in alunos_presentes_ids
            try:
                Presenca.objects.update_or_create(
                    matricula=matricula,
                    data=data_presenca,
                    turma_disciplina=turma_disciplina,
                    aula_numero=aula_numero,
                    defaults={'presente': presente, 'controle_diario': False}
                )                
            except Exception as e:
                print(f"Erro ao registrar presença para matrícula {matricula.id}: {e}")
        messages.success(request, "Frequência diária realizada com sucesso!!!")
        return redirect('modulo_professor:faltas_por_disciplina_mes', turma_disciplina_id=turma_disciplina.id)

    # Envia a data atual formatada como dd/mm/aaaa
    today = date.today()
    data_formatada = today.strftime('%d/%m/%Y')

    return render(request, 'modulo_professor/partial/presenca/presenca_por_aula.html', {
    'matriculas': matriculas,
    'turma_disciplina': turma_disciplina,
    'data': data_formatada,
    'today': today,
    })


@login_required
def faltas_por_disciplina_mes_view(request, turma_disciplina_id):
    turma_disciplina = get_object_or_404(TurmaDisciplina, id=turma_disciplina_id)
    turma = turma_disciplina.turma
    matriculas = Matriculas.objects.filter(turma=turma)

    mes_param = request.GET.get('mes')
    if mes_param:
        try:
            mes = datetime.strptime(mes_param, "%Y-%m")
        except ValueError:
            mes = datetime.today()
    else:
        mes = datetime.today()

    inicio_mes = mes.replace(day=1)
    if mes.month == 12:
        fim_mes = mes.replace(year=mes.year + 1, month=1, day=1)
    else:
        fim_mes = mes.replace(month=mes.month + 1, day=1)

    presencas = Presenca.objects.filter(
        turma_disciplina=turma_disciplina,
        data__gte=inicio_mes,
        data__lt=fim_mes,
        presente=False
    ).order_by('data')

    # Armazena as faltas detalhadas: {matricula: [(data, numero_aula), ...]}
    faltas_detalhadas = defaultdict(list)
    for presenca in presencas:
        faltas_detalhadas[presenca.matricula].append((presenca.data, presenca.aula_numero))

    return render(request, 'modulo_professor/partial/presenca/faltas_por_disciplina_mes.html', {
        'turma_disciplina': turma_disciplina,
        'faltas_detalhadas': dict(faltas_detalhadas),
        'mes': mes.strftime('%Y-%m'),
        'hoje': date.today(),
    })


# Diario de Classe -----------------

class PlanoDeAulaForm(forms.ModelForm):
    class Meta:
        model = PlanoDeAula
        fields = '__all__'
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'conteudo_planejado': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'objetivo_geral': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'competencias_bncc': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'habilidades_bncc': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'metodologia': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'recursos_didaticos': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if request:
            escola = request.session.get('escola')
            user = request.user

            try:
                pessoa = UserPessoas.objects.get(user=user).pessoa
                encaminhamentos = Encaminhamentos.objects.filter(encaminhamento__contratado=pessoa)

                self.fields['turma_disciplina'].queryset = TurmaDisciplina.objects.filter(
                    Q(professor__in=encaminhamentos) |
                    Q(professo2__in=encaminhamentos) |
                    Q(reserva_tecnica__in=encaminhamentos) |
                    Q(auxiliar_classe__in=encaminhamentos),
                    turma__escola=escola
                ).distinct()

            except UserPessoas.DoesNotExist:
                self.fields['turma_disciplina'].queryset = TurmaDisciplina.objects.none()




from django.db.models import Q
from modulo_professor.models import TurmaDisciplina
from rh.models import UserPessoas, Encaminhamentos

from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from modulo_professor.models import TurmaDisciplina, PlanoDeAula
from rh.models import UserPessoas, Encaminhamentos, Contrato


class PlanoDeAulaCreateView(LoginRequiredMixin, CreateView):
    model = PlanoDeAula
    form_class = PlanoDeAulaForm
    template_name = 'modulo_professor/partial/diario/planoAula/createPlano.html'
    success_url = reverse_lazy('modulo_professor:plano_de_aula_criar')  # redireciona para mesma view

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = self.request.session.get('escola')
        usuario = self.request.user
        pessoa = get_object_or_404(UserPessoas, user = usuario)

        if escola and usuario:
            try:
                pessoa = UserPessoas.objects.get(user=usuario).pessoa
            except UserPessoas.DoesNotExist:
                pessoa = None

            if pessoa:
                planos = PlanoDeAula.objects.filter(
                    turma_disciplina__professor__encaminhamento__contratado__id=pessoa.id,
                    turma_disciplina__turma__escola__id=escola.id
                ).distinct()
            else:
                planos = PlanoDeAula.objects.none()
        else:
            planos = PlanoDeAula.objects.none()

        context['planos'] = planos
        return context


    def form_valid(self, form):
        print("FORM VALID - POST recebido com sucesso!")
        response = super().form_valid(form)
        messages.success(self.request, "Plano de aula salvo com sucesso!")
        return response
    
    def form_invalid(self, form):
        # Captura os nomes legíveis dos campos com erro
        campos_com_erro = [form.fields[field].label or field for field in form.errors]

        # Cria uma mensagem amigável
        mensagem = "Por favor, é preciso preencher os seguintes campos obrigatórios: " + ", ".join(campos_com_erro)

        # Envia a mensagem de erro para o usuário
        messages.error(self.request, mensagem)
        return super().form_invalid(form)






from django.views.generic import UpdateView, DeleteView
from django.urls import reverse_lazy

class PlanoDeAulaUpdateView(LoginRequiredMixin, UpdateView):
    model = PlanoDeAula
    form_class = PlanoDeAulaForm
    template_name = 'modulo_professor/partial/diario/planoAula/createPlano.html'
    success_url = reverse_lazy('modulo_professor:plano_de_aula_criar') 

    def form_valid(self, form):
        response = super().form_valid(form)
        obj = form.instance
        messages.success(
            self.request,
            f'O plano de aula de {obj.data_inicio} a {obj.data_fim} para {obj.turma_disciplina} foi atualizado com sucesso.'
        )
        return response


class PlanoDeAulaDeleteView(LoginRequiredMixin, DeleteView):
    model = PlanoDeAula
    template_name = 'modulo_professor/partial/diario/planoAula/plano_de_aula_confirm_delete.html'
    success_url = reverse_lazy('modulo_professor:plano_de_aula_criar') 

    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f'O plano de aula de {obj.data_inicio} a {obj.data_fim} para {obj.turma_disciplina} foi excluído com sucesso.')
        return super().delete(request, *args, **kwargs)



# ----------------- AULA DIA ----------------------------------
class AulaDadaForm(forms.ModelForm):
    class Meta:
        model = AulaDada
        fields = ['plano', 'turma_disciplina', 'aula_numero','data', 'hora_inicio', 'hora_fim', 'conteudo_dado', 'observacoes']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fim': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if request:
            escola = request.session.get('escola')
            user = request.user

            try:
                pessoa = UserPessoas.objects.get(user=user).pessoa
                encaminhamentos = Encaminhamentos.objects.filter(encaminhamento__contratado=pessoa)

                turmas_do_professor = TurmaDisciplina.objects.filter(
                    Q(professor__in=encaminhamentos) |
                    Q(professo2__in=encaminhamentos) |
                    Q(reserva_tecnica__in=encaminhamentos) |
                    Q(auxiliar_classe__in=encaminhamentos),
                    turma__escola=escola
                ).distinct()

                self.fields['turma_disciplina'].queryset = turmas_do_professor
                self.fields['plano'].queryset = PlanoDeAula.objects.filter(turma_disciplina__in=turmas_do_professor)

            except UserPessoas.DoesNotExist:
                self.fields['turma_disciplina'].queryset = TurmaDisciplina.objects.none()
                self.fields['plano'].queryset = PlanoDeAula.objects.none()


from collections import OrderedDict
from itertools import groupby
from operator import attrgetter
from django.contrib.messages.views import SuccessMessageMixin

class AulaDadaCreateView(LoginRequiredMixin, CreateView, SuccessMessageMixin):
    model = AulaDada
    form_class = AulaDadaForm    
    template_name = 'modulo_professor/partial/diario/aulaDia/criarAulaDia.html'
    success_url = reverse_lazy('modulo_professor:aula_dada_criar')

    def form_valid(self, form):
        messages.success(self.request, "Aula registrada com sucesso!")  
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs    
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = self.request.session.get('escola')
        usuario = self.request.user
        pessoa = get_object_or_404(UserPessoas, user = usuario)

        if escola and usuario:
            try:
                pessoa = UserPessoas.objects.get(user=usuario).pessoa
            except UserPessoas.DoesNotExist:
                pessoa = None

            if pessoa:
                planos = AulaDada.objects.filter(
                    plano__turma_disciplina__professor__encaminhamento__contratado__id=pessoa.id,
                    turma_disciplina__turma__escola__id=escola.id
                ).distinct().order_by('-id')
            else:
                planos = AulaDada.objects.none()
        else:
            planos = AulaDada.objects.none()

        # Agrupando por plano
        aula_agrupada_por_plano = OrderedDict()
        for plano, aulas in groupby(planos, key=attrgetter('plano')):
            aula_agrupada_por_plano[plano] = list(aulas)

        context['aulas_agrupadas'] = aula_agrupada_por_plano
    
        return context
    




class AulaDadaDetailView(DetailView):
    model = AulaDada
    template_name = 'modulo_professor/aula_dada_detail.html'
    context_object_name = 'aula'

class AnexoAulaForm(forms.ModelForm):
    class Meta:
        model = AnexoAula
        fields = ['arquivo', 'descricao']

class AnexoAulaCreateView(CreateView):
    model = AnexoAula
    form_class = AnexoAulaForm
    template_name = 'modulo_professor/anexo_aula_form.html'

    def form_valid(self, form):
        form.instance.aula_id = self.kwargs['pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('modulo_professor:aula_dada_detalhe', kwargs={'pk': self.kwargs['pk']})







def detalhar_aula(request, aula_id):
    aula = get_object_or_404(AulaDada, id=aula_id)

    # Buscar todas as presenças para a aula específica
    presencas = Presenca.objects.filter(
        turma_disciplina=aula.turma_disciplina,
        #aula_numero = aula.aula_numero,
        data=aula.data,
        aula_numero=aula.aula_numero
    ).select_related('matricula__aluno')

    presentes = presencas.filter(presente=True)
    faltaram = presencas.filter(presente=False)

    context = {
        'aula': aula,
        'presentes': presentes,
        'faltaram': faltaram,
    }

    return render(request, 'modulo_professor/partial/diario/aulaDia/detalhar_aula.html', context)












def aulas_do_dia(request):
    hoje = timezone.now().date()

    # Busca todas as aulas dadas hoje
    aulas_hoje = AulaDada.objects.filter(data=hoje).select_related('plano', 'turma_disciplina')

    contexto_aulas = []

    for aula in aulas_hoje:
        # Presenças associadas à turma e data
        presencas = Presenca.objects.filter(
            turma_disciplina=aula.turma_disciplina,
            data=aula.data
        ).select_related('matricula__aluno')

        presentes = [p.matricula.aluno for p in presencas if p.presente]
        faltosos = [p.matricula.aluno for p in presencas if not p.presente]

        contexto_aulas.append({
            'aula': aula,
            'plano': aula.plano,
            'presentes': presentes,
            'faltosos': faltosos,
        })

    return render(request, 'modulo_professor/partial/diario/aulas_do_dia.html', {
        'aulas': contexto_aulas,
        'data_hoje': hoje,
    })

