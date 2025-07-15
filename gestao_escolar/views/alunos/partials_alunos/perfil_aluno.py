from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import DetailView
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import redirect

from gestao_escolar.models import Alunos, Matriculas, GestaoTurmas, Trimestre
from rh.models import Ano
from collections import defaultdict

class PerfilAluno(LoginRequiredMixin, SuccessMessageMixin, DetailView):
    model = Alunos
    template_name = 'Escola/inicio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        aluno = self.object
        ano_letivo_nome = self.request.session.get('anoLetivo_nome')
        ano = None

        if ano_letivo_nome:
            ano = Ano.objects.filter(ano=ano_letivo_nome).first()

        matriculas = Matriculas.objects.filter(aluno=aluno.id)
        boletim_raw = GestaoTurmas.objects.filter(
            aluno__aluno=aluno.id,
            aluno__turma__ano_letivo=ano
        ).select_related('grade__disciplina', 'trimestre')

        boletim_dict = defaultdict(lambda: {'notas': {}, 'faltas': {}})

        for entry in boletim_raw:
            nome_disciplina = entry.grade.disciplina.nome
            trimestre_nome = entry.trimestre.numero_nome
            boletim_dict[nome_disciplina]['notas'][trimestre_nome] = entry.notas
            boletim_dict[nome_disciplina]['faltas'][trimestre_nome] = entry.faltas
          
        context['trimestres'] = Trimestre.objects.filter(final = False)
        context.update({
            'matriculas': matriculas,
            'boletim_dict': dict(boletim_dict),
            'titulo_page': 'Alunos',
            'sub_titulo_page': 'Perfil do Aluno',
            'conteudo_page': 'Registrar Alunos',
            'sub_Info_page': "Extra",
            'sub_Info_page_h4': "INFORMAÇÕES EXTRA DO ALUNO",
            'oculta_tab': "true",
            'table': True,
            'bottom': "Salvar informações extras do aluno",
        })

        return context
