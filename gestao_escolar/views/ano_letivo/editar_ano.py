from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rh.models import Ano, Escola
from django import forms
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class AnoForm(forms.ModelForm):
    class Meta:
        model = Ano
        fields = [ 'data_inicio', 'data_fim']
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
        }


@login_required
def editar_ano(request, ano_id):
    ano = get_object_or_404(Ano, id=ano_id)

    if request.method == 'POST':
        form = AnoForm(request.POST, instance=ano)
        if form.is_valid():
            form.save()
            messages.success(request, '✏️ Ano Letivo atualizado com sucesso! As mudanças foram aplicadas.')
            return redirect('Gestao_Escolar:cria_ano')  # Redireciona para a listagem ou página de criação
    else:
        form = AnoForm(instance=ano)
        messages.info(request, f'Área de edição do Ano Letivo de {ano} acessada com sucesso.')

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
            'anos': Ano.objects.filter(prefeitura__id=escola),
            'ano': ano,
            'conteudo_page': 'criar Ano Letivo',
            'title_page': "<b>Editar Ano Letivo</b>",
            'form': form
        }
    else:
        context = {
            'form': form
        }   

    return render(request, 'Escola/inicio.html', context)
