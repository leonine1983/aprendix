from gestao_escolar.models import Matriculas, Turmas
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from datetime import datetime, date
from django.urls import reverse_lazy
from .matriculas_form import Turma_form


class Delete_Turmas(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Matriculas
    template_name = 'Escola/inicio.html'
    success_message = "Deletado com sucesso"
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')


    def get_context_data(self, **kwargs):
        svg = '<i class="fa-sharp fa-solid fa-people fs-5"></i>'
        aluno = self.object
        aluno_turma = self.object.turma
        context = super().get_context_data(**kwargs) 
        context['oculta_tab'] = "true"
        context['titulo_page'] = 'Excluir Matrícula'
        context['sub_Info_page'] = f"Você tem certerza que deseja excluir a matrícula de <b class='text-capitalize '>{aluno}</b> do {aluno_turma}"
        context['table'] = True   
        context['bottom'] = "Deletar"   
        context['btn_bg'] = " btn-danger "  
        #context['now'] = datetime.now()
        context['conteudo_page'] = 'delete'               
        context['page_ajuda'] = "<div class='border bg-secondary p-2'><h2>Pessoar a ser contratada</h2><div>"        
        return context   