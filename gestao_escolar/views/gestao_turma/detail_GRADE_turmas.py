from gestao_escolar.models import  Turmas
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime
from django.urls import reverse_lazy
from django.db.models import Q



class ViewTurmasGrade(LoginRequiredMixin, ListView):
    model = Turmas
    template_name = 'Escola/inicio.html'
    context_object_name = 'turmas'

    def get_queryset(self):
        """Filtra turmas por ano letivo e escola, com busca opcional por nome."""
        ano_letivo_id = self.request.session.get("anoLetivo_id")
        escola_id = self.request.session.get("escola_id")
        busca_turma = self.request.GET.get("busca-turma")

        filtros = Q(ano_letivo=ano_letivo_id, escola=escola_id)
        if busca_turma:
            filtros &= Q(nome__icontains=busca_turma)

        return Turmas.objects.filter(filtros)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # SVG decorativo (pode ser passado para o template ou usado em um include)
        svg_icon = (
            '<svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48">'
            '<path d="M38-160v-94q0-35 18-63.5t50-4B8r3B4..."/>'  # Truncado por clareza
            '</svg>'
        )

        context.update({
            'titulo_page': 'Grade de Disciplinas',
            'svg': svg_icon,
            'now': datetime.now(),
            'conteudo_page': "Todas as turmas-grade",
            'page_ajuda': self._get_ajuda_html()
        })

        return context

    def _get_ajuda_html(self):
        """Retorna o conteúdo HTML da seção de ajuda."""
        return """
        <div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional. </b>
        <hr>
            <div class='border bg-secondary p-2'>
                <h2>Pessoa a ser contratada</h2>
                <p>Selecione o nome da pessoa a ser contratada. Se estiver vazio: 
                   <a class='btn btn-sm btn-primary' href='pessoas/create/'>Cadastrar pessoa</a></p>
            </div>
            <div class='p-2'>
                <h2>Ano de contrato</h2>
                <p>Selecione o ano do contrato. Se estiver vazio: 
                   <a class='btn btn-sm btn-secondary' href='ano/create/'>Cadastrar ano</a></p>
            </div>
            <div class='border bg-secondary p-2'>
                <h2>Tipo de contrato</h2>
                <p>Escolha o modelo de contrato. Se estiver vazio: 
                   <a class='btn btn-sm btn-primary' href='ano/create/'>Criar modelo</a></p>
            </div>
            <div class='p-2'>
                <h2>Função na escola</h2>
                <p>Defina a função que o profissional irá exercer na instituição.</p>
            </div>
            <div class='border bg-secondary p-2'>
                <h2>Escola de atuação</h2>
                <p>Selecione a escola onde o profissional atuará. Se estiver vazio: 
                   <a class='btn btn-sm btn-primary' href='escola/create/'>Adicionar escola</a></p>
            </div>
        </div>
        """


"""
class View_turmas_Grade(LoginRequiredMixin, ListView ):
    model = Turmas
    #form_class = Turma_form
    template_name = 'Escola/inicio.html'

    def get_queryset(self):
        buscar_turma = self.request.GET.get ('busca-turma')
        if buscar_turma:
            turmas = Turmas.objects.filter(Q(ano_letivo = self.request.session["anoLetivo_id"]) and Q (escola = self.request.session["escola_id"] ))
        else:
            turmas = Turmas.objects.filter(ano_letivo = self.request.session["anoLetivo_id"], escola = self.request.session["escola_id"])
        return turmas

    def get_context_data(self, **kwargs):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48"><path d="M38-160v-94q0-35 18-63.5t50-4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM9-103.5T622-423q69 8 130 23.5t99 35.5q33 19 52 47t19 63v94H738ZM358-481q-66 0-108-4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM94B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM90 108 4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM96-23 21t-9 31v34Zm260-321q39 0 64.5-25.5T448-631q0-39-25.5-64.5T358-721q-39 0-64.5 25.5T268-631q0 39 25.5 64.5T358-541Zm0 321Zm0-411Z"/></svg>'
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Grade de Disciplinas'          
        context['svg'] = svg 
        context['turmas'] = self.get_queryset
        context['now'] = datetime.now()
        context['conteudo_page'] = "Todas as turmas-grade"       
        
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional. </b>\
            <hr>\
                <div class='border bg-secondary p-2'>\
                    <h2>Pessoar a ser contratada</h2>\
                    <p>Espaço onde é selecionado no nome da pessoa que será contratada. Se por alguma razão estiver vazio, clique aqui: <a class='btn btn-sm btn-primary' href='pessoas/create/'>Clique aqui para cadastrar uma pessoa no sistema</a></p>\
                </div>\
                <div class=' p-2'>\
                    <p><h2>Ano de contrato</h2>\
                    <p>Espaço onde é selecionado o ano em que o profissional será contratado. Se por alguma razão estiver vazio, clique aqui: <a class='btn btn-sm btn-secondary' href='ano/create/'>Clique aqui para cadastrar um ANO no sistema</a></p>\
                </div>\
                <div class='border bg-secondary p-2'>\
                    <p><h2>Tipo de contrato</h2>\
                    <p>Espaço onde é selecionado o modelo de contrato que será utilizado para a contratação. Se estiver vazio,  clique aqui: <a class='btn btn-sm btn-primary' href='ano/create/'>Clique aqui para criar um MODELO DE CONTRATO no sistema</a></p>\
                </div>\
                <div class=' p-2'>\
                    <p><h2>Função que irá desempenhar na escola</h2>\
                    <p>Local em que é definido a função pela qual o profissional está sendo contratado</p>\
                </div>\
                <div class='border bg-secondary p-2'>\
                    <p><h2>Escola onde o profissional irá desempenhar suas funções</h2>\
                    <p>Espaço onde é selecionado a instituição que o profissional desempenhará suas funções. Se estiver vazio,  clique aqui: <a class='btn btn-sm btn-primary' href='escola/create/'>Clique aqui para Adicionar uma Escola</a></p>\
                </div>"
        
        return context
       """     



            