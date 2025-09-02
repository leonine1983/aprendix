from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from gestao_escolar.models import Turmas
from rh.models import Ano, Escola

def exportar_turmas(request):
    escola = request.session['escola_id']
    if request.method == "POST":
        escola_id = escola
        ano_destino = request.POST.get("ano_origem")        

        escola = get_object_or_404(Escola, id=escola_id)

        # Recupera na sessão o ano letivo atual
        anoAtual = request.session['anoLetivo_nome']
        anoAnterior = get_object_or_404(Ano, ano = anoAtual)

        # Recupera o ano de destino
        ano_letivo_destino = get_object_or_404(Ano, id=ano_destino)

        # Recupera turmas do ano de origem
        turmas_origem = Turmas.objects.filter(escola=escola, ano_letivo=anoAnterior)
        print(f'turmas anterior {turmas_origem}')

        # Recupera turmas do ano de destino        
        turmas_destino = Turmas.objects.filter(escola=escola, ano_letivo=ano_letivo_destino)
        print(f'turmas destino {turmas_destino}')           

        if not turmas_origem.exists():
            messages.warning(request, "Nenhuma turma encontrada para exportar.")
            return redirect("Gestao_Escolar:exportar_turmas")

        # Prepara novas turmas
        if not turmas_destino:
            print(f'tem turmas')
            novas_turmas = []
            for turma in turmas_origem:
                novas_turmas.append(
                    Turmas(
                        nome=turma.nome,
                        descritivo_turma=turma.descritivo_turma,
                        escola=turma.escola,
                        ano_letivo=ano_letivo_destino,
                        serie=turma.serie,
                        turno=turma.turno,
                        turma_multiserie=turma.turma_multiserie,
                        turma_concluida=False,
                        quantidade_vagas=turma.quantidade_vagas,
                        vagas_disponiveis=turma.quantidade_vagas,
                    )
                )

            Turmas.objects.bulk_create(novas_turmas)

            messages.success(
                request,
                f"Turmas do ano {anoAnterior} exportadas com sucesso para {ano_letivo_destino}!"
            )
        else:
            messages.warning(
                request,
                f"⚠️ Já existem turmas cadastradas no ano letivo {ano_letivo_destino.ano} da escola {escola}. "
                f"Verifique esse ano letivo para confirmar se as turmas já foram criadas ou exportadas anteriormente."
            )

        return redirect("Gestao_Escolar:exportar_turmas")

    # Renderiza formulário
    escolas = Escola.objects.filter(id = escola)    
    anos = Ano.objects.all().order_by("-ano").first()
    explica = 'Este recurso permite duplicar todas as turmas de um ano letivo para o ano seguinte, garantindo a continuidade da organização escolar. Caso o próximo ano letivo ainda não exista, será criar um novo ano letivo antes da exportação'


    return render(request, "Escola/inicio.html", {
        "escolas": escolas, 
        "anos": anos,
        'titulo_page':'Exportar Turmas',  
        'sub_title_context':explica,     
        'conteudo_page':'exportar Turmas'    })
