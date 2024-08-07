from gestao_escolar.models import Matriculas
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy


class Delete_Matriculas(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Matriculas
    template_name = 'Escola/inicio.html'
    success_message = "Matrícul do aluno deletado com sucesso"
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')

    def get_context_data(self, **kwargs):
        aluno = self.object
        aluno_turma = self.object.turma
        context = super().get_context_data(**kwargs) 
        context['oculta_tab'] = "true"
        context['titulo_page'] = 'Excluir Matrícula'
        context['sub_Info_page'] = f"Você tem certerza que deseja excluir a matrícula de <b class='text-capitalize '>{aluno}</b> do {aluno_turma}"
        context['table'] = True   
        context['bottom'] = "Excluí matricula de"   
        context['btn_bg'] = " btn-danger " 
        context['conteudo_page'] = "matricula_update_or_delete"               
        context['page_ajuda'] = "<div class='border bg-secondary p-2'><h2>Pessoar a ser contratada</h2><div>"        
        return context   
    