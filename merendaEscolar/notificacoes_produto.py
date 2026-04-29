from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

from merendaEscolar.models import (
    EstoqueEscola,
    EstoqueCentral,
    Transferencia,
    DivergenciaEntrega
)
from merendaEscolar.models import Produto
from admin_acessos.models import NotificacaoProduto

User = get_user_model()


# ─────────────────────────────────────────────
# 👥 Usuários por escola (ajuste conforme regra institucional)
# ─────────────────────────────────────────────
def _usuarios_escola(escola):
    """
    Retorna usuários relacionados à escola.
    (Ajuste aqui se houver vínculo direto usuário-escola)
    """
    return User.objects.filter(is_active=True)


# ─────────────────────────────────────────────
# 🚫 Idempotência
# ─────────────────────────────────────────────
def _notificacao_existe(usuario, event_key):
    return NotificacaoProduto.objects.filter(
        usuario=usuario,
        event_key=event_key
    ).exists()


def _criar_notificacao(usuario, escola, titulo, mensagem, tipo, event_key):
    if not _notificacao_existe(usuario, event_key):
        NotificacaoProduto.objects.create(
            usuario=usuario,
            escola=escola,
            titulo=titulo,
            mensagem=mensagem,
            tipo=tipo,
            event_key=event_key
        )


# ─────────────────────────────────────────────
# 📉 ESTOQUE BAIXO (ESCOLA)
# ─────────────────────────────────────────────
def verificar_estoque_baixo(escola):

    estoques = (
        EstoqueEscola.objects
        .select_related("produto")
        .filter(escola=escola)
    )

    for item in estoques:

        if item.quantidade <= item.produto.estoque_minimo:

            event_key = f"estoque_baixo_{escola.id}_{item.produto.id}"

            titulo = f"Estoque baixo: {item.produto.nome}"

            mensagem = (
                f"O produto {item.produto.nome} está abaixo do mínimo.\n"
                f"Atual: {item.quantidade} | Mínimo: {item.produto.estoque_minimo}"
            )

            for usuario in _usuarios_escola(escola):
                _criar_notificacao(
                    usuario,
                    escola,
                    titulo,
                    mensagem,
                    "ESTOQUE_BAIXO",
                    event_key
                )


# ─────────────────────────────────────────────
# ⏰ VALIDADE (CENTRAL)
# ─────────────────────────────────────────────
def verificar_validade_produtos():

    hoje = timezone.now().date()

    estoques = (
        EstoqueCentral.objects
        .select_related("produto")
        .all()
    )

    for item in estoques:

        if not item.data_validade:
            continue

        dias = (item.data_validade - hoje).days

        # 🚨 VENCIDO
        if dias < 0:

            event_key = f"produto_vencido_{item.id}"

            titulo = f"Produto vencido: {item.produto.nome}"

            mensagem = (
                f"Lote {item.lote or 'Sem lote'} venceu em "
                f"{item.data_validade.strftime('%d/%m/%Y')}"
            )

        # ⚠️ CRÍTICO (até 7 dias)
        elif dias <= 7:

            event_key = f"produto_critico_{item.id}"

            titulo = f"Produto próximo do vencimento: {item.produto.nome}"

            mensagem = (
                f"Lote {item.lote or 'Sem lote'} vence em {dias} dia(s)"
            )

        else:
            continue

        for usuario in User.objects.filter(is_active=True):
            _criar_notificacao(
                usuario,
                None,
                titulo,
                mensagem,
                "PRODUTO_VENCENDO",
                event_key
            )


# ─────────────────────────────────────────────
# 🚚 TRANSFERÊNCIA ENVIADA
# ─────────────────────────────────────────────
def notificar_transferencia_enviada(transferencia: Transferencia):

    event_key = f"transferencia_enviada_{transferencia.id}"

    titulo = f"Transferência enviada: {transferencia.numero}"

    mensagem = (
        f"Transferência enviada para {transferencia.escola_destino.nome_escola}"
    )

    for usuario in _usuarios_escola(transferencia.escola_destino):
        _criar_notificacao(
            usuario,
            transferencia.escola_destino,
            titulo,
            mensagem,
            "TRANSFERENCIA_ENVIADA",
            event_key
        )


# ─────────────────────────────────────────────
# 📥 TRANSFERÊNCIA RECEBIDA
# ─────────────────────────────────────────────
def notificar_transferencia_recebida(transferencia: Transferencia):

    event_key = f"transferencia_recebida_{transferencia.id}"

    titulo = f"Transferência recebida: {transferencia.numero}"

    mensagem = "Transferência confirmada e integrada ao estoque."

    for usuario in _usuarios_escola(transferencia.escola_destino):
        _criar_notificacao(
            usuario,
            transferencia.escola_destino,
            titulo,
            mensagem,
            "TRANSFERENCIA_RECEBIDA",
            event_key
        )


# ─────────────────────────────────────────────
# ⚠️ DIVERGÊNCIA
# ─────────────────────────────────────────────
def notificar_divergencia(divergencia: DivergenciaEntrega):

    event_key = f"divergencia_{divergencia.id}"

    titulo = f"Divergência registrada: {divergencia.produto.nome}"

    mensagem = (
        f"Enviado: {divergencia.quantidade_enviada} | "
        f"Recebido: {divergencia.quantidade_recebida}"
    )

    for usuario in User.objects.filter(is_active=True):
        _criar_notificacao(
            usuario,
            divergencia.transferencia.escola_destino,
            titulo,
            mensagem,
            "DIVERGENCIA_ABERTA",
            event_key
        )