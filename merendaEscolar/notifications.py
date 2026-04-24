# merendaEscolar/notifications.py
import calendar
from datetime import date, timedelta

from django.contrib.auth.models import Group, User
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from merendaEscolar.models import Cardapio, CardapioDia, CardapioSemana
from admin_acessos.models import AtualizacaoNotificacaoSistema

DIAS_ESPERADOS = {1, 2, 3, 4, 5}  # seg a sex
AVISO_VENCIMENTO_DIAS = 7


def _nutricionistas():
    """Retorna todos os usuários ativos do grupo 'nutricionista'."""
    try:
        grupo = Group.objects.get(name="Nutricionista")
    except Group.DoesNotExist:
        return User.objects.none()
    return grupo.user_set.filter(is_active=True)


def _notificacao_existe(user, titulo):
    """Evita duplicar notificações já não-lidas com o mesmo título."""
    return AtualizacaoNotificacaoSistema.objects.filter(
        user=user, titulo=titulo, lida=False
    ).exists()


def _salvar_para_todos(titulo, mensagem, tipo):
    """Persiste a notificação para cada nutricionista (sem duplicar)."""
    for user in _nutricionistas():
        if not _notificacao_existe(user, titulo):
            AtualizacaoNotificacaoSistema.objects.create(
                user=user,
                titulo=titulo,
                mensagem=mensagem,
                tipo=tipo,
            )


# ─── verificações ────────────────────────────────────────────────────────────

def _verificar_vencimento(cardapio):
    """Avisa se o cardápio vence nos próximos AVISO_VENCIMENTO_DIAS dias."""
    hoje = date.today()
    delta = (cardapio.data_fim - hoje).days

    if delta < 0:
        titulo = f"Cardápio vencido: {cardapio.nome}"
        mensagem = (
            f"O cardápio <strong>{cardapio.nome}</strong> venceu em "
            f"{cardapio.data_fim.strftime('%d/%m/%Y')}. "
            f"As escolas vinculadas podem ficar sem cardápio ativo."
        )
        _salvar_para_todos(titulo, mensagem, "urgente")

    elif delta <= AVISO_VENCIMENTO_DIAS:
        titulo = f"Cardápio prestes a vencer: {cardapio.nome}"
        mensagem = (
            f"O cardápio <strong>{cardapio.nome}</strong> vence em "
            f"{cardapio.data_fim.strftime('%d/%m/%Y')} "
            f"({delta} dia(s)). Renove ou crie um novo cardápio para as escolas vinculadas."
        )
        _salvar_para_todos(titulo, mensagem, "aviso")


def _verificar_semanas_mes(cardapio):
    """
    Avisa se o mês do cardápio contém mais de 4 semanas ISO e o cardápio
    não possui semanas suficientes para cobrir todas elas.
    """
    # Conta semanas ISO distintas dentro do intervalo data_inicio..data_fim
    semanas_no_periodo = set()
    cursor = cardapio.data_inicio
    while cursor <= cardapio.data_fim:
        if cursor.weekday() < 5:  # apenas dias úteis
            semanas_no_periodo.add(cursor.isocalendar()[1])
        cursor += timedelta(days=1)

    total_semanas_necessarias = len(semanas_no_periodo)

    if total_semanas_necessarias <= 4:
        return  # situação normal, sem aviso

    semanas_cadastradas = cardapio.semanas.count()

    if semanas_cadastradas < total_semanas_necessarias:
        faltam = total_semanas_necessarias - semanas_cadastradas
        titulo = f"Semanas incompletas: {cardapio.nome}"
        mensagem = (
            f"O período do cardápio <strong>{cardapio.nome}</strong> cobre "
            f"<strong>{total_semanas_necessarias} semanas</strong>, mas apenas "
            f"{semanas_cadastradas} foram cadastradas. "
            f"Faltam <strong>{faltam} semana(s)</strong>. "
            f"As escolas vinculadas podem ficar sem cardápio em alguns dias."
        )
        _salvar_para_todos(titulo, mensagem, "aviso")


def _verificar_dias_faltando(cardapio):
    """
    Para cada semana do cardápio, verifica se todos os dias úteis
    (seg–sex) foram cadastrados. Emite um aviso por semana incompleta.
    """
    for semana in cardapio.semanas.prefetch_related("dias").all():
        dias_cadastrados = set(
            semana.dias.values_list("dia_semana", flat=True)
        )
        dias_faltando = DIAS_ESPERADOS - dias_cadastrados

        if not dias_faltando:
            continue

        NOMES_DIAS = {
            1: "Segunda", 2: "Terça", 3: "Quarta",
            4: "Quinta",  5: "Sexta",
        }
        dias_str = ", ".join(
            NOMES_DIAS[d] for d in sorted(dias_faltando)
        )
        titulo = f"Dias faltando — {cardapio.nome} (Semana {semana.numero})"
        mensagem = (
            f"A <strong>Semana {semana.numero}</strong> do cardápio "
            f"<strong>{cardapio.nome}</strong> não possui os seguintes dias: "
            f"<strong>{dias_str}</strong>. "
            f"As escolas vinculadas ficarão sem cardápio nesses dias."
        )
        _salvar_para_todos(titulo, mensagem, "aviso")


# ─── entrada principal ────────────────────────────────────────────────────────

def verificar_cardapios_pendentes():
    """
    Ponto de entrada: itera todos os cardápios ativos e dispara
    as três verificações independentes.
    """
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


# ─── signal ───────────────────────────────────────────────────────────────────

@receiver(user_logged_in)
def ao_fazer_login(sender, request, user, **kwargs):
    """
    Dispara as verificações apenas quando um nutricionista faz login.
    Executado de forma síncrona (sem Celery) — adequado para volumes pequenos.
    """
    if user.groups.filter(name="Nutricionista").exists():
        verificar_cardapios_pendentes()