from django.shortcuts import redirect
from gestao_escolar.models import *
from django.views.generic import TemplateView
from rh.models import Escola, Encaminhamentos
from gestao_escolar.models import Alunos, Turmas, EscolaMatriculaOnline
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
import plotly.graph_objects as go
from django.db.models import Count
from django import forms
from gestao_escolar.models import MatriculasOnline
from django.contrib import messages

class MatriculasOnlineForm(forms.ModelForm):
    class Meta:
        model = MatriculasOnline
        fields = ['id','impugnar', 'pendecia']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pendecia'].label = (
            'Por favor, descreva as pendências que precisam ser resolvidas para a finalização '
            'da matrícula ou que precisam ser entregues durante a primeira semana de aula. '
            'Isso pode incluir documentos pendentes, requisitos administrativos ou qualquer outro '
            'item que precise ser entregue ou regularizado.'
        )
        self.fields['impugnar'].label = ("Clique no botão 'Impugnar' para informar que a matrícula não pode"
                                         " ser confirmada e, em seguida, descreva o motivo no campo abaixo. ")

    

class Pagina_inicio(LoginRequiredMixin, TemplateView):
    model = Escola
    template_name = 'Escola/inicio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_page'] = 'Selecione o ano letivo'
        context['svg'] = '<svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48"><path d="..."/></svg>'
        context['now'] = datetime.now()
        context['conteudo_page'] = 'info_escola'

        # Obter a escola do banco de dados
        sessao_escola = self.request.session['escola_id']
        escola = Escola.objects.get(id=sessao_escola)
        context['contexto'] = escola

        # Carregar o formulário de matrícula com dados existentes, se houver
        matricula_id = self.request.GET.get('matricula_id')
        if matricula_id:
            try:
                matricula = MatriculasOnline.objects.get(id=matricula_id)
                print(f'olhaaaaa a {matricula}')
                form = MatriculasOnlineForm(instance=matricula)  # Carrega os dados da matrícula existente
                context['form'] = form
            except MatriculasOnline.DoesNotExist:
                messages.error(self.request, 'Matrícula não encontrada.')
                context['form'] = MatriculasOnlineForm()  # Caso não exista matrícula, exibe um formulário vazio
        else:
            matricula = MatriculasOnline.objects.filter(serie__escola__ativo = True)
            context['form'] = MatriculasOnlineForm()  # Formulário vazio para nova matrícula

        # Carregar os alunos e encaminhamentos
        context['condicional_aluno'] = Alunos.objects.all()
        context['condicional_professor'] = Encaminhamentos.objects.all()

        # Informações para a área de ajuda
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."

        # Carregar turmas e gerar gráfico de matrícula
        turmas = Turmas.objects.prefetch_related('related_matricula_turma').filter(escola=escola, ano_letivo=self.request.session['anoLetivo_id'])
        context['condicional_turma'] = turmas
        
        turma_counts = turmas.annotate(num_matriculas=Count('related_matricula_turma'))
        a = [f'{t.nome} {t.descritivo_turma.upper()}' for t in turma_counts]
        b = [t.num_matriculas for t in turma_counts]
        cores = ['orange', 'green', 'red', 'blue', 'purple', 'cyan', 'magenta', 'yellow', 'black', 'pink', 'brown', 'gray', 'lime', 'teal', 'indigo']
        
        fig = go.Figure(data=go.Bar(x=a, y=b, marker_color=cores))
        fig.update_layout(title='Gráfico das Turmas', xaxis_title='Turmas', yaxis_title='Número de Matrículas')
        graph_html = fig.to_html(full_html=False)
        context['graph'] = graph_html

        # Exibir matrícula pública
        matPublica = MatriculasOnline.objects.filter(serie__escola__escola__id=escola.id, serie__escola__ativo=True)
        context['escolaMatriculaOnline'] = matPublica if matPublica else {}

        return context

    def post(self, request, *args, **kwargs):
        if 'matricula_id' in request.POST:
            matricula_id = request.POST['matricula_id']
            try:
                matricula = MatriculasOnline.objects.get(id=matricula_id)
                form = MatriculasOnlineForm(request.POST, instance=matricula)  # Preenche o formulário com a matrícula existente
                if form.is_valid():
                    form.save()  # Atualiza a matrícula no banco
                    messages.success(request, 'Matrícula atualizada com sucesso!')
                    return redirect('Gestao_Escolar:GE_Escola_inicio')
                else:
                    messages.error(request, 'Erro ao atualizar a matrícula.')
            except MatriculasOnline.DoesNotExist:
                messages.error(request, 'Matrícula não encontrada.')

        return redirect('Gestao_Escolar:GE_Escola_inicio')
