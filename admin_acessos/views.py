from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView, DetailView
from django.views import View
from django import forms
from ckeditor.widgets import CKEditorWidget

from .models import MessageUser, PaletaCores

# Login
class CreateLoginView(LoginView):
    template_name = 'admin_acessos/index.html'
    success_url = reverse_lazy('admin_acessos:painel_acesso')

    def form_invalid(self, form):
        messages.error(self.request, 'Credenciais inválidas. Por favor, tente novamente.')
        return super().form_invalid(form)

# Logout
class LogoutView(LogoutView):
    next_page = reverse_lazy('admin_acessos:login_create')

    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return super().dispatch(request, *args, **kwargs)

# Painel de Acesso
class PainelAcessoView(TemplateView):
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
