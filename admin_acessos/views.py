from django.shortcuts import  redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView, DetailView
from django.views import View
from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import MessageUser, PaletaCores
from django.contrib.auth.models import User, Group

# Login
import random

class CreateLoginView(LoginView):
    template_name = 'Admin_Acessos/index.html'

    def form_invalid(self, form):
        messages.error(self.request, 'Credenciais inválidas. Por favor, tente novamente.')
        return super().form_invalid(form)

    def get_success_url(self):
        name = self.request.user.username.capitalize()
        mensagens_boas_vindas = [
            f'Sabe {name}, \'A educação é a arma mais poderosa que você pode usar para mudar o mundo.\' - Nelson Mandela',
            f'{name}, \'O sucesso é ir de fracasso em fracasso sem perder o entusiasmo.\' - Winston Churchill',
            f'Olá {name}, \'A mente que se abre a uma nova ideia jamais voltará ao seu tamanho original.\' - Albert Einstein',
            f'{name}, \'A persistência é o caminho do êxito.\' - Charles Chaplin',
            f'{name}, \'Aprender é a única coisa de que a mente nunca se cansa, nunca tem medo e nunca se arrepende.\' - Leonardo da Vinci',
            f'{name}, \'Se você quer alcançar a grandeza, pare de pedir permissão.\' - Autor desconhecido',
            f'Bem-vindo {name}, \'A única coisa que interfere com meu aprendizado é a minha educação.\' - Albert Einstein',
            f'{name}, \'Coragem é a resistência ao medo, domínio do medo – não a ausência do medo.\' - Mark Twain',
            f'{name}, \'Seja a mudança que você deseja ver no mundo.\' - Mahatma Gandhi',
            f'{name}, \'A alegria de fazer o bem é a única felicidade verdadeira.\' - Léon Tolstói',
            f'{name}, \'Você nunca será velho demais para estabelecer um novo objetivo ou sonhar um novo sonho.\' - C.S. Lewis',
            f'{name}, \'A melhor maneira de prever o futuro é criá-lo.\' - Peter Drucker',
            f'{name}, \'Não é o mais forte que sobrevive, nem o mais inteligente, mas o que melhor se adapta às mudanças.\' - Charles Darwin',
            f'{name}, \'A vida é 10% o que acontece com você e 90% como você reage a isso.\' - Charles R. Swindoll',
            f'{name}, \'O único lugar onde o sucesso vem antes do trabalho é no dicionário.\' - Vidal Sassoon',
            f'{name}, \'A dúvida é um traidor que nos faz perder o bem que poderíamos conquistar, por medo de tentar.\' - William Shakespeare',
            f'{name}, \'Tudo parece impossível até que seja feito.\' - Nelson Mandela',
            f'{name}, \'Conhece-te a ti mesmo e conhecerás o universo e os deuses.\' - Sócrates',
            f'{name}, \'A motivação é o que te faz começar. O hábito é o que te mantém em movimento.\' - Jim Ryun',
            f'{name}, \'A educação é o passaporte para o futuro, pois o amanhã pertence àqueles que se preparam hoje.\' - Malcolm X',
            f'{name}, \'O que quer que você faça, faça-o bem.\' - Abraham Lincoln',
            f'{name}, \'A disciplina é a mãe do sucesso.\' - Ésquilo',
            f'{name}, \'Não é suficiente fazer o seu melhor; você deve saber o que fazer e então fazer o seu melhor.\' - W. Edwards Deming',
            f'{name}, \'Grandes realizações não são feitas por impulso, mas por uma soma de pequenas realizações.\' - Vincent van Gogh',
            f'{name}, \'Não espere por oportunidades extraordinárias. Agarre ocasiões comuns e torne-as grandes.\' - Orison Swett Marden',
            f'{name}, \'A mente é tudo. Você se torna aquilo que você pensa.\' - Buda',
            f'{name}, \'Nada é particularmente difícil se você o dividir em pequenas tarefas.\' - Henry Ford',
            f'{name}, \'Não se preocupe com fracassos; preocupe-se com as chances que você perde quando nem tenta.\' - Jack Canfield',
            f'{name}, \'A educação não transforma o mundo. Educação muda pessoas. Pessoas transformam o mundo.\' - Paulo Freire',
            f'{name}, \'Todos os nossos sonhos podem se realizar, se tivermos coragem de persegui-los.\' - Walt Disney',
            f'{name}, \'A simplicidade é o último grau de sofisticação.\' - Leonardo da Vinci',
            f'{name}, \'O único modo de fazer um excelente trabalho é amar o que você faz.\' - Steve Jobs',
            f'{name}, \'O aprendizado nunca esgota a mente.\' - Leonardo da Vinci',
            f'{name}, \'As raízes da educação são amargas, mas o fruto é doce.\' - Aristóteles',
            f'{name}, \'A verdadeira viagem do descobrimento não consiste em procurar novas paisagens, mas em ter novos olhos.\' - Marcel Proust',
            f'{name}, \'A dúvida é o princípio da sabedoria.\' - Aristóteles',
            f'{name}, \'Não podemos resolver nossos problemas com o mesmo pensamento que usamos quando os criamos.\' - Albert Einstein',
            f'{name}, \'Nada é tão contagioso quanto o exemplo.\' - François de La Rochefoucauld',
            f'{name}, \'A ação é a chave fundamental para todo sucesso.\' - Pablo Picasso',
            f'{name}, \'Você é aquilo que faz repetidamente. Excelência, então, não é um ato, mas um hábito.\' - Aristóteles',
            f'{name}, \'Nunca é tarde para ser aquilo que você poderia ter sido.\' - George Eliot',
            f'{name}, \'As melhores e mais belas coisas do mundo não podem ser vistas nem tocadas. Elas devem ser sentidas com o coração.\' - Helen Keller',
            f'{name}, \'A sabedoria começa na reflexão.\' - Confúcio',
            f'{name}, \'A jornada de mil milhas começa com um único passo.\' - Lao Tsé',
            f'{name}, \'Viver é a coisa mais rara do mundo. A maioria das pessoas apenas existe.\' - Oscar Wilde',
            f'{name}, \'A leitura de todos os bons livros é como uma conversa com as melhores mentes dos séculos passados.\' - René Descartes',
            f'{name}, \'Quando você quer alguma coisa, todo o universo conspira para que você realize seu desejo.\' - Paulo Coelho',
            f'{name}, \'O futuro pertence àqueles que acreditam na beleza de seus sonhos.\' - Eleanor Roosevelt',
            f'{name}, \'A felicidade é a única coisa que se multiplica quando é dividida.\' - Albert Schweitzer'
        ]        
        mensagem = random.choice(mensagens_boas_vindas)
        mensagem = mensagem.format(self.request.user.first_name)
        messages.info(self.request, f'<i class="fa-duotone fa-solid fa-hand-wave fa-shake fs-1"></i> {mensagem}')

        if self.request.user.groups.filter(name='Aluno').exists():
            return reverse_lazy('modulo_aluno:homeAluno')        
        elif self.request.user.groups.filter(name='Professor').exists():
            return reverse_lazy('modulo_professor:homeProfessor')                
        else:
            return reverse_lazy('Gestao_Escolar:GE_inicio')



# Logout
class LogoutView_logout(LogoutView):
    next_page = reverse_lazy('admin_acessos:painel_acesso')    
    success_url = reverse_lazy('admin_acessos:login_create')

    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return super().dispatch(request, *args, **kwargs)
    

# Painel de Acesso
class PainelAcessoView(LoginRequiredMixin, TemplateView):
    template_name = 'admin_acessos/features/panel_acesso.html'


# Message User Form
class MessageUserForm(forms.ModelForm):
    mensagem = forms.CharField(widget=CKEditorWidget())  # Atualizado para o campo correto

    class Meta:
        model = MessageUser
        fields = ['destinatario', 'assunto', 'mensagem']  # Removido 'user' e ajustado para refletir os campos do modelo
        widgets = {
            'remetente': forms.HiddenInput(),  # Manter o remetente como um campo oculto
        }


# Create Message
class MensagemCreateView(CreateView):
    model = MessageUser
    form_class = MessageUserForm
    template_name = 'Controle_Estoque/mensagem/mensagem_envia.html'
    success_url = reverse_lazy("admin_acessos:mensagem_lista")

    def form_valid(self, form):
        mensagem = form.save(commit=False)
        mensagem.remetente = self.request.user
        mensagem.save()
        return super().form_valid(form)
    

# List Messages
class MensagemListView(ListView):
    model = MessageUser
    template_name = 'Controle_Estoque/mensagem/mensage_lista.html'

    def get_queryset(self):
        return MessageUser.objects.filter(user=self.request.user)
    

# Update Message
class MensagemUpdateView(UpdateView):
    model = MessageUser
    fields = '__all__'
    template_name = 'Controle_Estoque/mensagem/mensagem_envia.html'


# Delete Message
class MensagemDeleteView(DeleteView):
    model = MessageUser
    template_name = 'Controle_Estoque/mensagem/mensagem_envia.html'
    success_url = reverse_lazy('admin_acessos:mensagem_lista')


# Update Message Status
class UpdateMessageView(View):
    def get(self, request, *args, **kwargs):
        message_id = kwargs.get('pk')
        message = get_object_or_404(MessageUser, id=message_id)
        message.aberta = True
        message.save()
        return redirect(reverse('admin_acessos:mensagem_detalhe', args=[message_id]))
    

# Message Detail
class DetalheMensagemView(DetailView):
    model = MessageUser
    template_name = 'Controle_Estoque/mensagem/mensage_lista.html'
    context_object_name = 'mensagem'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["svg"] = '<svg class="bi" width="30" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512"><!-- SVG content --></svg>'
        context["title"] = 'Mensagem para o usuário'
        context['active'] = 'mensagem'
        context['tipo'] = 'visualiza'
        return context


# Paletas de Cores Views
class PaletaCoresListView(ListView):
    model = PaletaCores
    template_name = 'paletacores_list.html'

class PaletaCoresDetailView(DetailView):
    model = PaletaCores
    template_name = 'paletacores_detail.html'

class PaletaCoresCreateView(CreateView):
    model = PaletaCores
    template_name = 'paletacores_form.html'
    fields = ['nome_paleta', 'cor_primaria', 'cor_secundaria', 'cor_sucesso', 'cor_info', 'cor_aviso', 'cor_perigo', 'cor_texto']
    success_url = reverse_lazy('paletacores_list')

class PaletaCoresUpdateView(UpdateView):
    model = PaletaCores
    template_name = 'paletacores_form.html'
    fields = ['nome_paleta', 'cor_primaria', 'cor_secundaria', 'cor_sucesso', 'cor_info', 'cor_aviso', 'cor_perigo', 'cor_texto']
    success_url = reverse_lazy('paletacores_list')

class PaletaCoresDeleteView(DeleteView):
    model = PaletaCores
    template_name = 'paletacores_confirm_delete.html'
    success_url = reverse_lazy('paletacores_list')


# -----------Criar usuarios ---------------------------------
from django.contrib.auth.models import User
from rh.models import  EscolaUser, Escola

class UserCreationFormAll(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(), label='Senha')
    password2 = forms.CharField(widget=forms.PasswordInput(), label='Confirmar Senha')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', ]  # Inclua todos os campos desejados

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas não coincidem")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
    

class CreateUsers(LoginRequiredMixin, CreateView):
    model = User
    form_class = UserCreationFormAll
    template_name = 'Escola/inicio.html'

    def get_success_url(self):
        #return reverse_lazy('admin_acessos:CreateUsers')
        return reverse_lazy('Gestao_Escolar:GE_Escola_inicio')
    
    def form_valid(self, form):
        # Salva o objeto no banco de dados primeiro
        response = super().form_valid(form)
        user_pk = form.instance.pk

        school_pk = self.request.session['escola_id']
        escola = Escola.objects.get(pk=school_pk)
        user = User.objects.get(pk=user_pk)

        EscolaUser.objects.create(
            escola=escola,
            usuario=user
        )

        messages.success(
            self.request,
            f'Usuário {user.first_name or user.username} criado com sucesso e vinculado à escola "{escola.nome_escola}"!'
        )

        return response

    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        context['conteudo_page'] = 'create_users'   
        pk_school = self.request.session['escola_id']
        user = self.request.user
        if user.is_superuser:
            context['all_user_school'] = User.objects.all()  
        else:
            context['all_user_school'] = User.objects.filter(related_UserEscola__escola=pk_school)  
        return context
