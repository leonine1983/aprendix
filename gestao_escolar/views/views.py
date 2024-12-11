from django.shortcuts import redirect
from gestao_escolar.models import *
from django.views.generic import TemplateView
from rh.models import Escola, Encaminhamentos
from gestao_escolar.models import Alunos, Turmas, EscolaMatriculaOnline
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
import plotly.graph_objects as go
from django.db.models import Count


class Pagina_inicio(LoginRequiredMixin, TemplateView):
    model = Escola
    template_name = 'Escola/inicio.html'    

    def get(self, request, *args, **kwargs):
        if 'escola_id' in request.session: 
            return super().get(request, *args, **kwargs)
        else:
            return redirect('Gestao_Escolar:GE_inicio')

    def get_context_data(self, **kwargs):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48"><path d="M38-160v-94q0-35 18-63.5t50-4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM9-103.5T622-423q69 8 130 23.5t99 35.5q33 19 52 47t19 63v94H738ZM358-481q-66 0-108-4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM94B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM90 108 4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM96-23 21t-9 31v34Zm260-321q39 0 64.5-25.5T448-631q0-39-25.5-64.5T358-721q-39 0-64.5 25.5T268-631q0 39 25.5 64.5T358-541Zm0 321Zm0-411Z"/></svg>'
        
        context = super().get_context_data(**kwargs)
        context['titulo_page'] = 'Selecione o ano letivo'                   
        context['svg'] = svg 
        context['now'] = datetime.now()        
        context['conteudo_page'] = 'info_escola'   
        
        sessao_escola = self.request.session['escola_id']        

        # Obtenção direta da escola sem filtrar
        escola = Escola.objects.get(id=sessao_escola)
        context['contexto'] = escola
        
        # Evitar carregar todos os alunos e encaminhamentos, se possível
        context['condicional_aluno'] = Alunos.objects.all()  # Se necessário, limite as colunas
        context['condicional_professor'] = Encaminhamentos.objects.all()  # Idem
        
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."

        # Usando prefetch_related para otimizar o acesso a matrículas relacionadas
        turmas = Turmas.objects.prefetch_related('related_matricula_turma').filter(escola=escola, ano_letivo=self.request.session['anoLetivo_id'])  
        context['condicional_turma'] = turmas
        
        # Otimização da contagem de matrículas com annotate
        turma_counts = turmas.annotate(num_matriculas=Count('related_matricula_turma'))

        a = [f'{t.nome} {t.descritivo_turma.upper()}' for t in turma_counts]
        b = [t.num_matriculas for t in turma_counts]

        cores = [
            'orange', 'green', 'red', 'blue', 'purple', 'cyan', 'magenta', 'yellow', 
            'black', 'pink', 'brown', 'gray', 'lime', 'teal', 'indigo'
        ]

        # Criar o gráfico
        fig = go.Figure(data=go.Bar(x=a, y=b, marker_color=cores))
        fig.update_layout(
            title='Gráfico das Turmas',
            xaxis_title='Turmas',
            yaxis_title='Número de Matrículas'
        )      

        # Converter o gráfico para html
        graph_html = fig.to_html(full_html=False)
        context['graph'] = graph_html

        # Exibir matrícula pública
        matPublica = MatriculasOnline.objects.filter(serie__escola__escola__id=escola.id, serie__escola__ativo=True)
        context['escolaMatriculaOnline'] = matPublica if matPublica else {}

        return context
