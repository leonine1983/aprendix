from django.shortcuts import redirect
from django.urls import reverse_lazy
from gestao_escolar.models import *
from django.views.generic import TemplateView
from rh.models import Escola, Encaminhamentos
from gestao_escolar.models import Alunos, Turmas
from admin_acessos.models import AtualizacaoNotificacao
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
import plotly.graph_objects as go
from django import forms
from gestao_escolar.models import MatriculasOnline
from django.contrib import messages
from .contexto_dados_escolares import get_contexto_escola
from django.db.models import Count, Q
from gestao_escolar.views.gestao_turma.faltas import busca_ativa

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

    
from gestao_escolar.utils import processar_dados

class Pagina_inicio(LoginRequiredMixin, TemplateView):
    model = Escola
    template_name = 'Escola/inicio.html'

    def dispatch(self, request, *args, **kwargs):
        """       
        Verifica se a chave 'escola_id' está presente na sessão do usuário.

        Caso a chave 'escola_id' não esteja presente, o usuário é redirecionado para a 
        página inicial da gestão escolar ('Gestao_Escolar:GE_inicio'). Este controle 
        garante que o acesso à página inicial da escola só ocorra se uma escola estiver
        previamente selecionada na sessão.

        Retorna:
            HttpResponseRedirect: redirecionamento para a URL 'Gestao_Escolar:GE_inicio'
        """
        if 'escola_id' not in request.session:
            return redirect('Gestao_Escolar:GE_inicio')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """
        Monta o contexto para a página de início da escola, incluindo informações
        de matrículas, turmas, gráficos e notificações.
        """

        # =====================================================
        # 1️⃣ Dados de sessão e usuário
        # =====================================================
        ano = self.request.session.get('anoLetivo_id')
        escola_id = self.request.session.get('escola_id')
        user = self.request.user

        context = super().get_context_data(**kwargs)
        context['titulo_page'] = 'Selecione o ano letivo'
        context['svg'] = '<svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48"><path d="..."/></svg>'
        context['now'] = datetime.now()
        context['conteudo_page'] = 'info_escola'
        
        # Notificações não lidas para o usuário
        context['notifica'] = AtualizacaoNotificacao.objects.filter(user=user, lida=False)
        context['EnviaNotifica'] = AtualizacaoNotificacao.objects.filter(user=user, lida=False)

        # =====================================================
        # 2️⃣ Informações da escola
        # =====================================================
        context.update(get_contexto_escola(ano, escola_id))
        escola = Escola.objects.get(id=escola_id)
        context['contexto'] = escola

        # =====================================================
        # 3️⃣ Formulário de matrícula (novo ou existente)
        # =====================================================
        matricula_id = self.request.GET.get('matricula_id')
        if matricula_id:
            try:
                matricula = MatriculasOnline.objects.get(id=matricula_id)
                context['form'] = MatriculasOnlineForm(instance=matricula)
            except MatriculasOnline.DoesNotExist:
                messages.error(self.request, 'Matrícula não encontrada.')
                context['form'] = MatriculasOnlineForm()
        else:
            context['form'] = MatriculasOnlineForm()

        # =====================================================
        # 4️⃣ Dados auxiliares: alunos e encaminhamentos
        # =====================================================
        context['condicional_aluno'] = Alunos.objects.all()
        context['condicional_professor'] = Encaminhamentos.objects.all()
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."

        # =====================================================
        # 5️⃣ Turmas e gráfico de matrícula
        # =====================================================
        turmas = Turmas.objects.prefetch_related('related_matricula_turma').filter(
            escola=escola, ano_letivo=ano
        )
        context['condicional_turma'] = turmas

        turma_counts = turmas.annotate(num_matriculas=Count('related_matricula_turma'))
        nomes_turmas = [f'{t.nome} {t.descritivo_turma.upper()}' for t in turma_counts]
        matriculas_turmas = [t.num_matriculas for t in turma_counts]
        cores = ['orange', 'green', 'red', 'blue', 'purple', 'cyan', 'magenta', 'yellow', 'black', 'pink', 'brown', 'gray', 'lime', 'teal', 'indigo']

        fig = go.Figure(data=go.Bar(x=nomes_turmas, y=matriculas_turmas, marker_color=cores))
        fig.update_layout(title='Gráfico das Turmas', xaxis_title='Turmas', yaxis_title='Número de Matrículas')
        context['graph'] = fig.to_html(full_html=False)

        # =====================================================
        # 6️⃣ Matrículas públicas
        # =====================================================
        matPublica = MatriculasOnline.objects.filter(
            serie__escola__escola__id=escola.id, serie__escola__ativo=True
        )
        context['escolaMatriculaOnline'] = matPublica if matPublica else {}
        context['tem_pendente'] = matPublica.filter(confirma=False).exists()

        # =====================================================
        # 7️⃣ Turmas do próximo ano letivo
        # =====================================================
        turmas_proximo_ano = Turmas.objects.filter(ano_letivo__gt=ano, escola=escola).first()
        context['turmas_proximo_existem'] = turmas_proximo_ano

        turmas_proximo_ano = Turmas.objects.filter(ano_letivo__gt=ano, escola=escola).annotate(
            total_confirmados_online=Count(
                'serie__seriesOnlineRelated__related_serie_matricula',
                filter=Q(serie__seriesOnlineRelated__related_serie_matricula__confirma=True)
            ),
            total_online=Count('serie__seriesOnlineRelated__related_serie_matricula')
        )
        context['turmas_proximo_ano'] = turmas_proximo_ano

        # =====================================================
        # 8️⃣ Processamento de dados de matrículas (função externa)
        # =====================================================
        processar_dados(self.request, ano=ano, escola_id=escola_id)
        dados = processar_dados(self.request, ano, escola_id)
        context['matriculas_all'] = dados.get("matriculas_all", [])
        context['totais_vagas_disponiveis_total'] = dados.get("totais_vagas_disponiveis_total", {})

        # =====================================================
        # 9️⃣ Resumo detalhado de matrículas por turma
        # =====================================================
        matriculas_all = []
        totais_vagas_disponiveis_total = {
            'total_autistas': 0,
            'total_masculino': 0,
            'total_feminino': 0,
            'total_brancos': 0,
            'total_pardos': 0,
            'total_negros': 0,
            'total_amarelos': 0,
            'total_indigena': 0,
            'total_nDeclarados': 0,
            'total_pp': 0,
            'total_p': 0,
            'total_m': 0,
            'total_g': 0,
            'gg': 0,
            'total_turmas': 0,
            'total_vagas': 0,
            'total_matriculas': 0,
            'vagas_disponiveis_total': 0,
        }

        turmas = Turmas.objects.filter(escola=escola, ano_letivo=ano)
        turmas_info = []
        totais = totais_vagas_disponiveis_total.copy()

        for turma in turmas:
            # Estatísticas de alunos
            alunos_especiais = {
                'autistas': turma.related_matricula_turma.filter(aluno__espectro_autista=True).count(),
                'masculino': turma.related_matricula_turma.filter(aluno__sexo__nome='Masculino').count(),
                'feminino': turma.related_matricula_turma.filter(aluno__sexo__nome='Feminino').count(),
                'brancos': turma.related_matricula_turma.filter(aluno__etnia__nome='Branca').count(),
                'pardos': turma.related_matricula_turma.filter(aluno__etnia__nome='Parda').count(),
                'negros': turma.related_matricula_turma.filter(aluno__etnia__nome='Negra').count(),
                'amarelos': turma.related_matricula_turma.filter(aluno__etnia__nome='Amarela').count(),
                'indigenas': turma.related_matricula_turma.filter(aluno__etnia__nome='Indigena').count(),
                'nDeclarados': turma.related_matricula_turma.filter(aluno__etnia__nome='Não declarado').count(),
                'PP': turma.related_matricula_turma.filter(camisa_tamanho__nome='PP').count(),
                'P': turma.related_matricula_turma.filter(camisa_tamanho__nome='P').count(),
                'M': turma.related_matricula_turma.filter(camisa_tamanho__nome='M').count(),
                'G': turma.related_matricula_turma.filter(camisa_tamanho__nome='G').count(),
                'GG': turma.related_matricula_turma.filter(camisa_tamanho__nome='GG').count(),
            }

            # Atualiza totais gerais
            for k, v in alunos_especiais.items():
                key = f'total_{k.lower()}' if 'total_' + k.lower() in totais else k.lower()
                if key in totais:
                    totais[key] += v

            totais['total_turmas'] += 1
            totais['total_vagas'] += turma.quantidade_vagas
            totais['total_matriculas'] += turma.related_matricula_turma.count()
            totais['vagas_disponiveis_total'] = totais['total_vagas'] - totais['total_matriculas']

            # Adiciona dados da turma
            turmas_info.append({
                'nome': turma.nome,
                'descritivo_turma': turma.descritivo_turma,
                'matriculas': turma.related_matricula_turma.count(),
                'quantidade_vagas': turma.quantidade_vagas,
                'vagas_disponiveis': turma.vagas_disponiveis or turma.quantidade_vagas,
                **alunos_especiais
            })

        context["matriculas_all"] = turmas_info
        context["vagas_disponiveis_total"] = totais

        # Chama a função que retorna o contexto dos alunos em risco
        contexto_risco = obter_alunos_risco_evasao(self.request)

        # Atualiza o contexto da view com os dados retornados pela função
        context.update(contexto_risco)

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
