from ..models import DescarteEstoqueEscola
from merendaEscolar.models import MovimentacaoEstoque
from django.core.exceptions import ValidationError

@transaction.atomic
def descartar_produto_escola(estoque, quantidade, motivo, descricao, usuario):

    if quantidade > estoque.quantidade:
        raise ValidationError("Quantidade maior que o disponível em estoque.")

    # 🔻 baixa no estoque
    estoque.quantidade -= quantidade
    estoque.save()

    # 🧾 registro institucional
    descarte = DescarteEstoqueEscola.objects.create(
        escola=estoque.escola,
        estoque=estoque,
        produto=estoque.produto,
        lote=estoque.lote,
        quantidade=quantidade,
        motivo=motivo,
        descricao=descricao,
        registrado_por=usuario
    )

    # 📊 rastreabilidade no fluxo geral
    MovimentacaoEstoque.objects.create(
        produto=estoque.produto,
        escola=estoque.escola,
        quantidade=quantidade,
        tipo="SAIDA_ESCOLA",
        usuario=usuario,
        observacao=f"Descarte ({motivo}) - Lote {estoque.lote}"
    )

    return descarte