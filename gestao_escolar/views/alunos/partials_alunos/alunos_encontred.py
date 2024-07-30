from django.views.generic import TemplateView
from gestao_escolar.models import Alunos
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms

class MeuFormulario(forms.Form):
    nome_completo = forms.CharField(
        label='Nome Completo',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 text-info col m-2 rounded-1'}))
    nome_mae = forms.CharField(
        label='Nome da Mãe', 
        max_length=100,        
        widget=forms.TextInput(attrs={'class': 'form-control border border-info p-3 pb-3 text-info col m-2 rounded-1'}))

class AlunosEcontred(LoginRequiredMixin,TemplateView):    
    template_name = 'Escola/inicio.html'       

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nome_completo = self.kwargs.get('nome_completo')
        nome_mae = self.kwargs.get('nome_mae')
        print(f'Nome da mae : {nome_mae}')
        # Agora você pode usar 'nome_completo' no contexto conforme necessário
        # Preenche o formulário com os valores
        formulario = MeuFormulario(initial={'nome_completo': nome_completo, 'nome_mae': nome_mae})

        # Adiciona o formulário ao contexto
        context['form'] = formulario

        nome_completo_query = Alunos.objects.filter(nome_completo__icontains = nome_completo) 
        context['titulo_page'] = 'Alunos'        
        context['conteudo_page'] = 'Registrar Alunos'            
        context['sub_Info_page'] = "Foram encontrados os seguintes\
              nomes de alunos que se assemelham ao nome do aluno que\
                  você está tentando cadastrar. "
        context['sub_Info_page_h4'] = "Se você realmente deseja cadastrar o aluno, apesar do risco de duplicação, por favor, confirme os dados no formulário abaixo:"
        context['nome_completo'] = nome_completo_query
        context['oculta_tab'] = "true"
        context['danger'] = "bg-danger-subtle"
        context['aluno_encontred'] = True
      
        return context
    
    
