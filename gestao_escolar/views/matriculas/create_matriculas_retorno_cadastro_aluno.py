from gestao_escolar.models import Matriculas, Alunos, Turmas
from rh.models import Ano
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .matriculas_form import Matricula_form_retorno_aluno
from django.core.paginator import Paginator
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages


class Create_Matriculas_Retorno_alunos(LoginRequiredMixin, CreateView):
    model = Matriculas
    #fields = '__all__'
    form_class = Matricula_form_retorno_aluno
    template_name = 'Escola/inicio.html'
    
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs ['aluno'] = Alunos.objects.filter(pk = self.kwargs['pk'])
        escola_id = self.request.session['escola_id']

        ano_nome = self.request.session['anoLetivo_nome']
        ano = Ano.objects.get(ano=ano_nome)

        turma = Turmas.objects.filter(ano_letivo = ano.id, escola__id = escola_id)
        kwargs ['turma_queryset'] = turma
        return kwargs    
    
    def get_context_data(self, **kwargs):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48"><path d="M38-160v-94q0-35 18-63.5t50-4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM9-103.5T622-423q69 8 130 23.5t99 35.5q33 19 52 47t19 63v94H738ZM358-481q-66 0-108-4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM94B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM90 108 4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM96-23 21t-9 31v34Zm260-321q39 0 64.5-25.5T448-631q0-39-25.5-64.5T358-721q-39 0-64.5 25.5T268-631q0 39 25.5 64.5T358-541Zm0 321Zm0-411Z"/></svg>'
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Matrículas'          
        context['svg'] = svg 

        matriculas = Matriculas.objects.filter(turma =self.kwargs['pk'])
        paginato = Paginator(matriculas, per_page=15)
        page_number = self.request.GET.get('page')
        page_obj = paginato.get_page(page_number)

        context['matriculas'] = page_obj
        context['n_matriculas'] = matriculas
        context['aluno_M'] = Alunos.objects.get(pk = self.kwargs['pk'])
        context['turma_ativa'] = Turmas.objects.all()
        context['conteudo_page'] = "Turmas Escolha"  
        context['page_ajuda'] = "<div class='m-2'><b>Nessa área, definimos todos os dados para a celebração do contrato com o profissional."        
        return context
    
    def form_valid(self, form):
        # Obtenha o aluno do formulário
        aluno = form.cleaned_data['aluno']
        
        # Verifique se o aluno já está matriculado em alguma turma no ano letivo atual
        ano_atual = self.request.session.get('anoLetivo_id')  # Certifique-se de que 'anoLetivo_id' está definido na sessão
        matricula_existente = Matriculas.objects.filter(aluno=aluno, turma__ano_letivo_id=ano_atual).first()
        
        if matricula_existente:
            nome_escola = Matriculas.objects.filter(aluno=aluno, turma__ano_letivo_id=ano_atual)
            for n in nome_escola:
                escola = n.turma.escola
                turma =  n.turma.nome
                telefone = n.turma.escola.telefone_escola 
                endereço = n.turma.escola.endereco_escola 
            # Se já existe uma matrícula para o mesmo aluno e ano letivo, mostre uma mensagem de erro
            error_message = f'<h3>Este aluno já está matriculado no ano letivo atual.</h3>\
                            <div class="card w-50 m-auto">\
                                <div class="card-header fs-3">\
                                    <i class="fa-duotone fa-circle-info"></i> Informações sobre a escola\
                                </div>\
                                <div class="card-body fs-2 text-right">\
                                    <h3 class="text-uppercase text-success">{escola}</h3>\
                                    <p class="fs-2">Endereço: <b class="fs-3 ">{endereço}</b></p>\
                                    <p class="fs-2">Telefone <i class="fa-brands fa-whatsapp"></i>: <b class="fs-3">{telefone}</b></p>\
                                    <p class="fs-2">Turma: <b class="fs-3">{turma}</b></p>\
                                    <a href="#" class="btn btn-primary">\
                                        Atenção!! Antes de sair dessa tela, anote os dados da escola. Nâo será possivel consultar novamente\
                                    </a>\
                                </div>\
                            </div>\
            '
            messages.error(self.request, error_message)
            return redirect(reverse('Gestao_Escolar:GE_Escola_inicio'))  

        # Se o aluno ainda não estiver matriculado, prossiga com o salvamento do registro de matrícula
        aluno = form.instance.aluno
        messages.success(self.request, f"🎉 Parabéns! O aluno {aluno} foi matriculado com sucesso! 📝👏 " )        
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('Gestao_Escolar:GE_Escola_alunos_create')