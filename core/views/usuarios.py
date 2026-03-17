from django.views.generic import CreateView, UpdateView
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.contrib import messages
from django import forms

from core.models.perfil import PerfilUsuario


from django.views.generic import ListView
from django.contrib.auth import get_user_model
from django.db.models import Count, Max
from django.contrib import messages
from django.db.models import Q

from django.db.models import Count, Max, Q, Exists, OuterRef
from django.contrib.auth.models import Group

from core.permissions import GroupRequiredMixin
from core.models.acesso import HistoricoAcesso

User = get_user_model()


class UsuarioListView(GroupRequiredMixin, ListView):

    group_required = ("Nutricionista", "Admin")

    model = User
    template_name = "core/usuarios/lista.html"
    context_object_name = "usuarios"
    paginate_by = 20
    
    def get_queryset(self):

        busca = self.request.GET.get("q")

        grupo_nutricionista = Group.objects.filter(
            name="Nutricionista",
            user=OuterRef("pk")
        )

        grupo_merendeira = Group.objects.filter(
            name="Merendeira",
            user=OuterRef("pk")
        )

        queryset = (
            User.objects
            .exclude(is_superuser=True)
            .filter(
                groups__name__in=["Merendeira", "Nutricionista"]
            )
            .annotate(
                total_acessos=Count("acessos"),
                ultimo_acesso=Max("acessos__data_acesso"),

                # 🔥 Flags institucionais
                is_nutricionista=Exists(grupo_nutricionista),
                is_merendeira=Exists(grupo_merendeira),
            )
            .select_related("perfilusuario")
            .distinct()
            .order_by("first_name", "username")
        )

        if busca:
            queryset = queryset.filter(
                Q(first_name__icontains=busca) |
                Q(username__icontains=busca) |
                Q(email__icontains=busca)
            )

        return queryset

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")

        return context

    def get(self, request, *args, **kwargs):

        messages.info(
            request,
            "Lista institucional de usuários carregada."
        )

        return super().get(request, *args, **kwargs)


class UsuarioForm(forms.ModelForm):

    grupo = forms.ChoiceField(
        choices=(
            ("Nutricionista", "Nutricionista"),
            ("Merendeira", "Merendeira"),
        ),
        label="Grupo institucional"
    )

    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Senha"
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

            grupo_nome = self.cleaned_data["grupo"]
            grupo = Group.objects.get(name=grupo_nome)

            user.groups.clear()
            user.groups.add(grupo)

            PerfilUsuario.objects.get_or_create(user=user)

        return user


class UsuarioUpdateForm(forms.ModelForm):

    grupo = forms.ChoiceField(
        choices=(
            ("Nutricionista", "Nutricionista"),
            ("Merendeira", "Merendeira"),
        ),
        label="Grupo institucional"
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email"]

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.save()

            grupo_nome = self.cleaned_data["grupo"]
            grupo = Group.objects.get(name=grupo_nome)

            user.groups.clear()
            user.groups.add(grupo)

        return user


class UsuarioCreateView(GroupRequiredMixin, CreateView):

    group_required = ("Nutricionista", "Admin")

    model = User
    form_class = UsuarioForm
    template_name = "core/usuarios/form.html"
    success_url = reverse_lazy("core:usuarios_lista")

    def form_valid(self, form):

        response = super().form_valid(form)

        messages.success(
            self.request,
            "Usuário criado com sucesso."
        )

        return response

    def form_invalid(self, form):

        messages.error(
            self.request,
            "Erro ao criar usuário. Verifique os dados informados."
        )

        return super().form_invalid(form)


class UsuarioUpdateView(GroupRequiredMixin, UpdateView):

    group_required = ("Nutricionista", "Admin")

    model = User
    form_class = UsuarioUpdateForm
    template_name = "core/usuarios/form.html"
    success_url = reverse_lazy("core:usuarios_lista")

    def get_initial(self):

        initial = super().get_initial()

        grupo = self.object.groups.first()

        if grupo:
            initial["grupo"] = grupo.name

        return initial

    def form_valid(self, form):

        response = super().form_valid(form)

        messages.success(
            self.request,
            "Usuário atualizado com sucesso."
        )

        return response

    def form_invalid(self, form):

        messages.error(
            self.request,
            "Erro ao atualizar usuário."
        )

        return super().form_invalid(form)
    



from django.views.generic import DeleteView
from django.shortcuts import redirect
from django.contrib import messages


class UsuarioDeleteView(GroupRequiredMixin, DeleteView):

    group_required = ("Admin",)

    model = User
    success_url = reverse_lazy("core:usuarios_lista")

    def get_queryset(self):

        """
        Proteção institucional:
        impede exclusão de superusuários.
        """

        return User.objects.exclude(is_superuser=True)

    def post(self, request, *args, **kwargs):

        self.object = self.get_object()

        # Proteção: impedir excluir o próprio usuário
        if self.object == request.user:

            messages.error(
                request,
                "Não é permitido excluir o próprio usuário."
            )

            return redirect("core:usuarios_lista")

        nome = self.object.get_full_name() or self.object.username

        self.object.delete()

        messages.success(
            request,
            f"Usuário '{nome}' removido com sucesso."
        )

        return redirect(self.success_url)
    

from django.views.generic import UpdateView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages

from core.permissions import GroupRequiredMixin
from core.models.perfil import PerfilUsuario
from rh.models import Escola  # ajuste conforme seu app

from django import forms


class VincularUsuarioEscolaForm(forms.ModelForm):

    class Meta:
        model = PerfilUsuario
        fields = ["escola"]
        widgets = {
            "escola": forms.Select(attrs={
                "class": "form-select"
            })
        }
        labels = {
            "escola": "Escola vinculada"
        }


class VincularUsuarioEscolaView(GroupRequiredMixin, UpdateView):

    group_required = ("Nutricionista", "Admin")

    model = PerfilUsuario
    form_class = VincularUsuarioEscolaForm
    template_name = "core/usuarios/vincular_escola.html"
    success_url = reverse_lazy("core:usuarios_lista")

    def get_object(self, queryset=None):
        user_id = self.kwargs.get("pk")
        user = get_object_or_404(User, pk=user_id)

        perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
        return perfil

    def dispatch(self, request, *args, **kwargs):

        perfil = self.get_object()

        if not perfil.user.groups.filter(name="Merendeira").exists():

            messages.error(
                request,
                "Apenas usuários do grupo Merendeira podem ser vinculados a uma escola."
            )

            return redirect("core:usuarios_lista")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        response = super().form_valid(form)

        messages.success(
            self.request,
            "Usuário vinculado à escola com sucesso."
        )

        return response

    def form_invalid(self, form):

        messages.error(
            self.request,
            "Erro ao vincular usuário à escola."
        )

        return super().form_invalid(form)