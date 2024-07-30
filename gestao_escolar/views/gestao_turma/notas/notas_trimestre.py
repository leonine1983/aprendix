# views.py
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import generic
from gestao_escolar.models import GestaoTurmas, Matriculas, Trimestre, TurmaDisciplina
from .formsNotas import GestaoTurmasForm

class GestaoTurmasNotas(generic.CreateView):
    model = GestaoTurmas
    form_class = GestaoTurmasForm    
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('nome_da_sua_url_de_sucesso')  # Defina a URL de redirecionamento após o sucesso

    def get_initial(self):
        initial = super().get_initial()
        aluno_id = self.kwargs['aluno_id']
        initial['aluno'] = get_object_or_404(Matriculas, id=aluno_id)
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['disciplinas'] = TurmaDisciplina.objects.all()  
        context['conteudo_page'] = "Gestão Turmas - Notas Aluno"
        return context
