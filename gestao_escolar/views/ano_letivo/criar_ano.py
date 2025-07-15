from django.shortcuts import render, redirect
from rh.models import Ano, Escola
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django import forms
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class AnoForm(forms.ModelForm):
    class Meta:
        model = Ano
        fields = ['prefeitura', 'ano', 'data_inicio', 'data_fim']
        widgets = {
            'data_inicio': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'placeholder': 'dd/mm/aaaa'
                }
            ),
            'data_fim': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'placeholder': 'dd/mm/aaaa'
                }
            ),
            'ano': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ex: 2025'
                }
            ),
            'prefeitura': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            )
        }



@login_required
def cria_ano(request):
    if request.method == 'POST':
        form = AnoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '📚 O Ano Letivo foi registrado com sucesso. Organização e planejamento prontos para começar!')
            return redirect('Gestao_Escolar:cria_ano')
    else:
        form = AnoForm()

    esc_session = request.session.get('escola_nome')
    if esc_session:
        escola = Escola.objects.get(nome_escola=esc_session).prefeitura.id
        anos_queryset = Ano.objects.filter(prefeitura__id=escola).order_by('-ano')

        paginator = Paginator(anos_queryset, 8)  # 5 anos por página
        page = request.GET.get('page')
        try:
            anos = paginator.page(page)
        except PageNotAnInteger:
            anos = paginator.page(1)
        except EmptyPage:
            anos = paginator.page(paginator.num_pages)

        context = {
            'anos': anos,
            'conteudo_page': 'criar Ano Letivo',
            'title_page': "<b>Ano Letivo</b>",
            'form': form
        }
    else:
        context = {'form': form}

    return render(request, 'Escola/inicio.html', context)

