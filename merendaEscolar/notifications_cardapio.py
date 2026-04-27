from datetime import date, timedelta

from django.contrib.auth.models import Group, User
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone

from merendaEscolar.models import Cardapio
from admin_acessos.models import AtualizacaoNotificacaoSistema

# 🔥 NOVO IMPORT
from merendaEscolar.notificacoes_produto import verificar_validade_produtos


DIAS_ESPERADOS = {1, 2, 3, 4, 5}
AVISO_VENCIMENTO_DIAS = 7


# ─────────────────────────────────────────────
# 👥 Usuários Nutricionistas
# ─────────────────────────────────────────────
def _nutricionistas():
    try:
        grupo = Group.objects.get(name="Nutricionista")
    except Group.DoesNotExist:
        return User.objects.none()
    return grupo.user_set.filter(is_active=True)


# ─────────────────────────────────────────────
# 🚫 Idempotência
# ─────────────────────────────────────────────
def _notificacao_existe(user, event_key):
    return AtualizacaoNotificacaoSistema.objects.filter(
        user=user,
        event_key=event_key
    ).exists()


def _salvar_para_todos(titulo, mensagem, tipo, event_key):
    for user in _nutricionistas():
        if not _notificacao_existe(user, event_key):
            AtualizacaoNotificacaoSistema.objects.create(
                user=user,
                titulo=titulo,
                mensagem=mensagem,
                tipo=tipo,
                event_key=event_key
            )


# ─────────────────────────────────────────────
# 🔎 VERIFICAÇÕES DE CARDÁPIO
# ─────────────────────────────────────────────

def _verificar_vencimento(cardapio):
    hoje = date.today()
    delta = (cardapio.data_fim - hoje).days

    if delta < 0:
        titulo = f"Cardápio vencido: {cardapio.nome}"
        event_key = f"cardapio_vencido_{cardapio.id}"

        mensagem = (
            f"O cardápio <strong>{cardapio.nome}</strong> venceu em "
            f"{cardapio.data_fim.strftime('%d/%m/%Y')}."
        )

        _salvar_para_todos(titulo, mensagem, "urgente", event_key)

    elif delta <= AVISO_VENCIMENTO_DIAS:
        titulo = f"Cardápio prestes a vencer: {cardapio.nome}"
        event_key = f"cardapio_vencendo_{cardapio.id}"

        mensagem = (
            f"O cardápio <strong>{cardapio.nome}</strong> vence em "
            f"{cardapio.data_fim.strftime('%d/%m/%Y')} "
            f"({delta} dia(s))."
        )

        _salvar_para_todos(titulo, mensagem, "aviso", event_key)


def _verificar_semanas_mes(cardapio):
    semanas_no_periodo = set()
    cursor = cardapio.data_inicio

    while cursor <= cardapio.data_fim:
        if cursor.weekday() < 5:
            semanas_no_periodo.add(cursor.isocalendar()[1])
        cursor += timedelta(days=1)

    total_semanas = len(semanas_no_periodo)

    if total_semanas <= 4:
        return

    semanas_cadastradas = cardapio.semanas.count()

    if semanas_cadastradas < total_semanas:
        faltam = total_semanas - semanas_cadastradas

        titulo = f"Semanas incompletas: {cardapio.nome}"
        event_key = f"semanas_incompletas_{cardapio.id}"

        mensagem = (
            f"O período cobre {total_semanas} semanas, "
            f"mas apenas {semanas_cadastradas} cadastradas. "
            f"Faltam {faltam}."
        )

        _salvar_para_todos(titulo, mensagem, "aviso", event_key)


def _verificar_dias_faltando(cardapio):
    for semana in cardapio.semanas.prefetch_related("dias").all():

        dias_cadastrados = set(
            semana.dias.values_list("dia_semana", flat=True)
        )

        dias_faltando = DIAS_ESPERADOS - dias_cadastrados

        if not dias_faltando:
            continue

        NOMES_DIAS = {
            1: "Segunda", 2: "Terça", 3: "Quarta",
            4: "Quinta", 5: "Sexta",
        }

        dias_str = ", ".join(NOMES_DIAS[d] for d in sorted(dias_faltando))

        titulo = f"Dias faltando — {cardapio.nome} (Semana {semana.numero})"
        event_key = f"dias_faltando_{cardapio.id}_{semana.numero}"

        mensagem = f"Faltam os dias: {dias_str}"

        _salvar_para_todos(titulo, mensagem, "aviso", event_key)


# ─────────────────────────────────────────────
# 🚀 EXECUÇÃO PRINCIPAL
# ─────────────────────────────────────────────

def verificar_cardapios_pendentes():
    hoje = date.today()

    cardapios = (
        Cardapio.objects
        .filter(ativo=True, data_fim__gte=hoje - timedelta(days=1))
        .prefetch_related("semanas__dias")
    )

    for cardapio in cardapios:
        _verificar_vencimento(cardapio)
        _verificar_semanas_mes(cardapio)
        _verificar_dias_faltando(cardapio)


# ─────────────────────────────────────────────
# 🔔 SIGNAL (LOGIN)
# ─────────────────────────────────────────────

@receiver(user_logged_in)
def ao_fazer_login(sender, request, user, **kwargs):
    """
    Executa verificações institucionais no login.

    Regras:
    - Apenas nutricionista
    - Executa 1 vez por sessão
    """

    if not user.groups.filter(name="Nutricionista").exists():
        return

    # 🔐 Evita execução repetida na mesma sessão
    if request.session.get("auditoria_executada"):
        return

    # 🚀 Execução principal
    verificar_cardapios_pendentes()
    verificar_validade_produtos()

    # Marca sessão
    request.session["auditoria_executada"] = True