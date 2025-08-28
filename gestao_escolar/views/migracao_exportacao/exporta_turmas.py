from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from gestao_escolar.models import Turmas
from rh.models import Ano, Escola

def exportar_turmas(request):
    if request.method == "POST":
        escola_id = request.POST.get("escola")
        ano_origem = request.POST.get("ano_origem")

        escola = get_object_or_404(Escola, id=escola_id)

        # Recupera o ano de origem
        ano_letivo_origem = get_object_or_404(Ano, ano=ano_origem)

        # Calcula o ano de destino
        ano_destino_str = str(int(ano_origem) + 1)

        # Cria o ano destino se não existir
        ano_letivo_destino, created = Ano.objects.get_or_create(
            ano=ano_destino_str,
            defaults={"prefeitura": escola.prefeitura}  # mantém vínculo
        )

        # Recupera turmas do ano de origem
        turmas_origem = Turmas.objects.filter(escola=escola, ano_letivo=ano_letivo_origem)

        if not turmas_origem.exists():
            messages.warning(request, "Nenhuma turma encontrada para exportar.")
            return redirect("exportar_turmas")

        # Prepara novas turmas
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
            f"Turmas do ano {ano_origem} exportadas com sucesso para {ano_destino_str}!"
        )
        return redirect("exportar_turmas")

    # Renderiza formulário
    escolas = Escola.objects.all()
    anos = Ano.objects.all().order_by("-ano")
    return render(request, "turmas/exportar_turmas.html", {"escolas": escolas, "anos": anos})
