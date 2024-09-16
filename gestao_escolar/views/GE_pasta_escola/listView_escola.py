from rh.models import Escola
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime
from gestao_escolar.utils import processar_dados
from rh.models import Ano


class ListView_Escola(LoginRequiredMixin, TemplateView):
    model = Escola
    template_name = 'Escola/inicio.html'
    context_object_name = 'escolas'

    def get_context_data(self, **kwargs):

        ano_id = self.request.session.get('anoLetivo_id')
        escola_id = self.request.session.get('escola_id')
        if ano_id and escola_id:
            ano = Ano.objects.get(id=ano_id)  # Supondo que você tem um modelo Ano
            processar_dados(self.request, ano, escola_id)
        
        svg = '<svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48"><path d="M38-160v-94q0-35 18-63.5t50-4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM9-103.5T622-423q69 8 130 23.5t99 35.5q33 19 52 47t19 63v94H738ZM358-481q-66 0-108-4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM94B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM90 108 4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM96-23 21t-9 31v34Zm260-321q39 0 64.5-25.5T448-631q0-39-25.5-64.5T358-721q-39 0-64.5 25.5T268-631q0 39 25.5 64.5T358-541Zm0 321Zm0-411Z"/></svg>'
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Selecione uma escola'          
        context['svg'] = svg 
        context['now'] = datetime.now()        
        context['conteudo_page'] = 'Nome das Escolas'       
        context['help'] = 'Nome das Escolas'             
        context['page_ajuda'] = "<div class='m-2'>\
                                    <p>Oi! Precisa de ajuda <i class='fa-duotone fa-solid fa-message-question fs-2'></i></p>\
                                    <p>Eu sou o Professor Coruja, ou como gosto de ser chamado, ARISTO. Vou ser seu ajudante aqui no Aprendix.</p>\
                                    <p>Sempre que precisar de uma mãozinha, é só clicar no botão de ajuda e, em um piscar de olhos, estarei aqui para te ajudar! Se eu não conseguir resolver, vou chamar um colega para te dar uma força. <i class='fa-duotone fa-solid fa-hands-holding-heart'></i></p>\
                                    <p>Ah, e se eu estiver falando muito rápido, não se preocupe! Você pode usar os botões aqui embaixo para rever o que eu disse. Um abraço!</p>\
                                    <p>Para começar, clique na lista acima e escolha uma das escolas disponíveis para a sua conta. Aqui você verá todas as escolas vinculadas ao seu cadastro. Pode ser uma ou várias escolas.</p>\
                                    <p>Se houver muitas escolas, pode ser necessário digitar parte do nome da escola para encontrá-la. Se a escola não aparecer, entre em contato com o administrador para verificar o que pode ter dado errado.</p>\
                                </div>"
        user = self.request.user
        if user.is_superuser:
            context['object_list'] = Escola.objects.all()
        else:
            context['object_list'] = Escola.objects.filter(related_escolaUser__usuario = user.id)
        
        return context
            



            