from rh.models import Profissao
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView
#from forms.profissao_form import Profissao_form
from django.urls import reverse_lazy


class Profissao_createView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Profissao
    fields = '__all__'
    #form_class = Profissao_form
    template_name = 'rh/inicio.html'
    success_url = reverse_lazy('RH:Profissao_listaView')
    success_message = 'Profissão criado com sucesso!!'

    def get_context_data(self, **kwargs):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 448 512"><!--! Font Awesome Free 6.4.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M224 256A128 128 0 1 1 224 0a128 128 0 1 1 0 256zM209.1 359.2l-18.6-31c-6.4-10.7 1.3-24.2 13.7-24.2H224h19.7c12.4 0 20.1 13.6 13.7 24.2l-18.6 31 33.4 123.9 36-146.9c2-8.1 9.8-13.4 17.9-11.3c70.1 17.6 121.9 81 121.9 156.4c0 17-13.8 30.7-30.7 30.7H285.5c-2.1 0-4-.4-5.8-1.1l.3 1.1H168l.3-1.1c-1.8 .7-3.8 1.1-5.8 1.1H30.7C13.8 512 0 498.2 0 481.3c0-75.5 51.9-138.9 121.9-156.4c8.1-2 15.9 3.3 17.9 11.3l36 146.9 33.4-123.9z"/></svg>'
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Profissões'          
        context['svg'] = svg 
        context['conteudo_page'] = 'Criar Profissão'        
        context['lista_profissoes'] = Profissao.objects.all()
        
        context['page_ajuda'] = "<div class='m-2'><b>Profissão </b>é uma ocupação que exige conhecimentos especializados, educação formal e habilidades específicas. Profissionais aderem a códigos de ética, fornecem serviços essenciais à sociedade e tomam decisões autônomas. A remuneração e o reconhecimento estão frequentemente ligados ao alto padrão de qualidade mantido. Isso envolve um compromisso de longo prazo com o desenvolvimento contínuo de habilidades.</div>\
            <div class='m-2 mt-5'><h2 class='h2'>Como prencher o formulário: <b>CRIAR PROFISSÃO</b><hr></h2>\
                <p><b>Profissão:</b> Preencha com o nome da profissão que deseja criar no sistema.</p>\
                    <p><b>Descreva a profissão:</b> Atribua uma descrição à criação profissão que está sendo criada, de maneira que\
                        as pessoas que fazer uso dela no sistema saiba, de fato, as atribuições dessa profissão.</p></div>"


        return context