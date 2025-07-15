from django.forms import BaseForm
from django.http.response import HttpResponse
from gestao_escolar.models import Matriculas
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy
import random


class Delete_Matriculas(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Matriculas
    template_name = 'Escola/inicio.html'
    success_url = reverse_lazy('Gestao_Escolar:GE_Escola_inicio')

    def form_valid(self, form: BaseForm):
        # Lista de mensagens de cancelamento
        mensagens_cancelamento = [
            "🚫 A matrícula do aluno foi cancelada com sucesso! 😓 Estamos prontos para ajudar no que for necessário e garantir que tudo se resolva. 💪 Caso precise de mais informações, estamos à disposição! 🤝",
            "❌ A matrícula do aluno foi cancelada. 😔 Mas não se preocupe, estamos aqui para apoiar você em qualquer necessidade. Fique à vontade para nos procurar! 💡",
            "🔴 A matrícula do aluno foi cancelada! Embora não tenha sido possível prosseguir, nosso time está disponível para qualquer dúvida ou ajuda que precisar. 🤗",
            "🚫 A matrícula foi cancelada! 😓 Se precisar de mais assistência ou quiser tentar novamente, estamos aqui para ajudar! 👥💬",
            "⚠️ A matrícula do aluno foi cancelada com sucesso. Se tiver alguma dúvida ou quiser refazer o processo, nossa equipe está pronta para ajudar! 💪",
            "🙅‍♂️ Matrícula do aluno cancelada! Mas não se preocupe, temos total disposição para resolver qualquer situação. Entre em contato conosco! 📞",
            "🔄 A matrícula do aluno foi cancelada. Se precisar de mais informações ou refazer a matrícula, nossa equipe está aqui para ajudar! 🤝",
            "⚠️ O processo de matrícula foi cancelado. Se precisar de assistência ou desejar tentar novamente, estamos à disposição para apoiar você! 👨‍🏫",
            "💔 A matrícula do aluno foi cancelada, mas não se preocupe! Se precisar de ajuda para refazer a matrícula ou para qualquer outra dúvida, estamos aqui para ajudar. 🤝",
            "🔔 A matrícula foi cancelada com sucesso. Se tiver algum questionamento ou precisar refazer a matrícula, nossa equipe está à disposição para te ajudar! 💬"
        ]
        msg = random.choice(mensagens_cancelamento)
        messages.warning(self.request, msg)
        aluno = self.object.aluno
        messages.success(self.request, f'Matrícula do aluno {aluno} foi cancelada com sucesso')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        aluno = self.object
        aluno_turma = self.object.turma
        context = super().get_context_data(**kwargs) 
        context['oculta_tab'] = "true"
        context['titulo_page'] = 'Excluir Matrícula'
        context['sub_Info_page'] = f"Você tem certerza que deseja excluir a matrícula de <b class='text-capitalize '>{aluno}</b> do {aluno_turma}"
        context['table'] = True   
        context['bottom'] = "Confirmar cancelamento de matrícula"  
        context['buttom_color'] = "btn-danger"   
        context['btn_bg'] = " btn-danger " 
        context['conteudo_page'] = "matricula_update_or_delete"               
        context['page_ajuda'] = "<div class='border bg-secondary p-2'><h2>Pessoar a ser contratada</h2><div>"        
        return context   
    