from rh.models import Escola
from gestao_escolar.models import  Matriculas, AnoLetivo, Turmas, Alunos
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy, reverse
from .matriculas_form import Matricula_form
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect


class Create_Matriculas(LoginRequiredMixin, SuccessMessageMixin, CreateView, ):
    model = Matriculas
    success_message = "Aluno matriculado com sucesso!!!"
    #fields = '__all__'
    form_class = Matricula_form
    template_name = 'Escola/inicio.html'    

    def get_success_url(self):
        turma = self.object.turma.id
        print (f'essa é a turma {turma}')
        return reverse_lazy('Gestao_Escolar:GE_Escola_Matricula_create', kwargs={'pk': turma}) 
    

    # envio_form Envia as informações de TURMA, ALUNOS para o form e ignora os alunos que ja estiverem matriculados
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs ['turma_queryset'] = Turmas.objects.filter(pk = self.kwargs['pk'])
        aluno_da_turma = Matriculas.objects.filter(turma = self.kwargs['pk']).values_list('id', flat=True)      
        todos  = Alunos.objects.exclude(id__in = aluno_da_turma)       
        kwargs ['aluno_query'] = todos
        return kwargs
    # /envio_form
    
    # search Faz a pesquisa de alunos na turma
    def get_queryset(self):
        txt_aluno = self.request.GET.get('busca-aluno')
        busca = False
        if txt_aluno:
            alunos = Matriculas.objects.filter(Q(turma__id =self.kwargs['pk']) and Q(aluno__nome_completo__icontains = txt_aluno))
            busca = True
        else:
            alunos = Matriculas.objects.filter(turma =self.kwargs['pk'])
            busca = False
        return alunos, busca
    # /search
    
    def get_context_data(self, **kwargs):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48"><path d="M38-160v-94q0-35 18-63.5t50-4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM9-103.5T622-423q69 8 130 23.5t99 35.5q33 19 52 47t19 63v94H738ZM358-481q-66 0-108-4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM94B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM90 108 4B8r3B4p7yhRXuBWLqsQ546WR43cqQwrbXMDFnBi6vSJBeif8tPW85a7r7DM961Jvk4hdryZoByEp8GC8HzsqJpRN4FxGM96-23 21t-9 31v34Zm260-321q39 0 64.5-25.5T448-631q0-39-25.5-64.5T358-721q-39 0-64.5 25.5T268-631q0 39 25.5 64.5T358-541Zm0 321Zm0-411Z"/></svg>'
        context = super().get_context_data(**kwargs)        
        context['titulo_page'] = 'Matrículas'          
        context['svg'] = svg 

        # Essa condiçao verifica o valor da variavel busca acessada no metodo get_queryset que retorna alunos, busca
        alunos, busca = self.get_queryset()
        if busca:
            matriculas = alunos
            context['matriculas'] = matriculas
        else:
            matriculas = Matriculas.objects.filter(turma =self.kwargs['pk'])
            paginato = Paginator(matriculas, per_page=9)
            page_number = self.request.GET.get('page')
            page_obj = paginato.get_page(page_number)
            context['matriculas'] = page_obj
        
        context['n_matriculas'] = matriculas
        #context['now'] = datetime.now()
        context['serie_multi'] = Turmas.objects.get(pk = self.kwargs['pk']).turma_multiserie
        context['turma_ativa'] = Turmas.objects.get(pk = self.kwargs['pk'])   
        context['conteudo_page'] = "Matricular Aluno"               
        context['page_ajuda'] = "<div class='border bg-secondary p-2'><h2>Pessoar a ser contratada</h2><div>"        
        return context   
        
    
    def form_valid(self, form):        
        # GERAR CODIDO DE MATICULA ----------
        ano_atual = self.request.session['anoLetivo_nome']
        # Usar o startswith para consultar somente os registros que tem a inicial igual ao ano letivo atual
        codigo_matricula_atual = Matriculas.objects.filter(cod_matricula__startswith = f'{ano_atual}-')
        # Determinar o proximo numero sequencial
        if codigo_matricula_atual.exists():
            ultimo_numero = int(codigo_matricula_atual.order_by('-cod_matricula').first().cod_matricula.split('-')[1])
            proximo_numero = ultimo_numero + 1
        else:
            proximo_numero = 1
        # Formatar o codigo
        novo_codigo = f'{ano_atual}-{proximo_numero:07d}'
        form.instance.cod_matricula = novo_codigo
        # / ----------

        
        form_data = self.request.POST    
        # Imprima os dados do formulário
        print("Dados do Formulário:")
        for key, value in form_data.items():
            print(f"{key}: {value}")
        # Chame o método da superclasse para definir self.object
        self.object = form.save(commit=False)  # Isso pode variar com base na lógica do seu formulário

        if self.object:
            matricula_exist = Matriculas.objects.filter(aluno=self.object.aluno, turma__ano_letivo=self.request.session['anoLetivo_id'])
            matricula_exist = matricula_exist.exclude(pk=self.object.pk) if self.object.pk else matricula_exist
            if matricula_exist.exists():
                for n in matricula_exist:
                    matricula_aluno = n.aluno
                    matricula_sexo = n.aluno.sexo.id
                    if matricula_sexo == 2:
                        sexo = 'a'
                    else:
                        sexo = 'o' 
                    matricula_turma = n.turma
                    matricula_escola = n.turma.escola
                    matricula_ano = n.turma.ano_letivo
                messages.error(self.request, f"{sexo} alun{sexo} <span class='text-capitalize'>{matricula_aluno}</span> já está matriculado na turma do {matricula_turma}</br> Escola {matricula_escola}, no Ano Letivo {matricula_ano}") 
                return redirect(reverse('Gestao_Escolar:GE_Escola_Matricula_create', kwargs={'pk': self.kwargs['pk']}))                
        return super().form_valid(form)
