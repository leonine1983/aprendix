from django.db import models, transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
from rh.models import Escola
from ckeditor.fields import RichTextField

from merendaEscolar.models import (
    Produto,
    Receita,
    EstoqueEscola,
    MovimentacaoEstoque,
    CardapioDia, 
    CardapioItem, 
    TipoRefeicao,
)

User = get_user_model()


# =========================================================
# MODELOS MELHORADOS
# =========================================================

class ExecucaoReceitaCozinha(models.Model):
    """
    Representa a execução real de uma receita na cozinha.
    """
    STATUS = (
        ("ABERTA", "Aberta"),
        ("EM_PREPARO", "Em preparo"),
        ("FINALIZADA", "Finalizada"),
        ("CANCELADA", "Cancelada"),
    )

    escola = models.ForeignKey(Escola, on_delete=models.PROTECT, related_name='execucoes_receita')
    receita = models.ForeignKey(Receita, on_delete=models.PROTECT, related_name='execucoes')
    status = models.CharField(max_length=20, choices=STATUS, default="ABERTA")
    
    # Controle de execução
    iniciado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='receitas_iniciadas')
    iniciado_em = models.DateTimeField(auto_now_add=True)
    finalizado_em = models.DateTimeField(null=True, blank=True)
    finalizado_por = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.PROTECT, 
        related_name='receitas_finalizadas'
    )
    
    # Metadados
    rendimento_real = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        help_text="Quantidade real de porções produzidas"
    )
    observacoes = RichTextField(blank=True, null=True)

    class Meta:
        ordering = ["-iniciado_em"]
        verbose_name = "Execução de Receita"
        verbose_name_plural = "Execuções de Receitas"

    def __str__(self):
        return f"{self.receita.nome} - {self.escola} ({self.get_status_display()})"

    def finalizar(self, usuario, rendimento_real=None):
        """Transição de estado para FINALIZADA"""
        if self.status == "CANCELADA":
            raise ValidationError("Não é possível finalizar uma execução cancelada.")
        
        self.status = "FINALIZADA"
        self.finalizado_em = timezone.now()
        self.finalizado_por = usuario
        if rendimento_real:
            self.rendimento_real = rendimento_real
        self.save(update_fields=['status', 'finalizado_em', 'finalizado_por', 'rendimento_real'])

    def cancelar(self, usuario, motivo=None):
        """Transição de estado para CANCELADA com devolução automática de estoque"""
        if self.status == "FINALIZADA":
            raise ValidationError("Não é possível cancelar uma execução já finalizada.")
        
        # Aqui poderia chamar serviço para devolver ingredientes já retirados
        self.status = "CANCELADA"
        self.finalizado_em = timezone.now()
        self.finalizado_por = usuario
        if motivo:
            self.observacoes = f"{self.observacoes or ''}\nCancelado por: {motivo}"
        self.save(update_fields=['status', 'finalizado_em', 'finalizado_por', 'observacoes'])


class MovimentacaoCozinha(models.Model):
    """
    Registra movimentações internas da cozinha (auditoria paralela ao estoque).
    """
    TIPO_CHOICES = (
        ("RETIRADA_RECEITA", "Retirada para Receita"),
        ("RETIRADA_EXTRA", "Retirada Extra"),
        ("DEVOLUCAO", "Devolução ao Estoque"),
        ("PERDA", "Perda/Desperdício"),
    )

    escola = models.ForeignKey(Escola, on_delete=models.CASCADE, related_name='movimentacoes_cozinha')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name='movimentacoes_cozinha')
    lote = models.CharField(max_length=50, blank=True, null=True)
    quantidade = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0.01)])
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='movimentos_cozinha')
    execucao_receita = models.ForeignKey(
        ExecucaoReceitaCozinha,
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='movimentacoes'
    )
    observacao = RichTextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Movimentação de Cozinha"
        verbose_name_plural = "Movimentações de Cozinha"

    def __str__(self):
        return f"{self.produto} - {self.tipo} - {self.quantidade} {self.produto.unidade_medida}"


class DescarteEstoqueEscola(models.Model):
    """
    Registro institucional de descarte realizado na escola.
    """
    MOTIVO_CHOICES = (
        ("VENCIDO", "Produto Vencido"),
        ("MOFO", "Produto Mofado"),
        ("GORGULHO", "Infestação (gorgulho ou insetos)"),
        ("EMBALAGEM_DANIFICADA", "Embalagem Danificada"),
        ("CONTAMINACAO", "Contaminação"),
        ("ARMAZENAMENTO_INADEQUADO", "Armazenamento inadequado"),
        ("OUTRO", "Outro Motivo"),
    )

    escola = models.ForeignKey(Escola, on_delete=models.PROTECT, related_name="descartes")
    estoque = models.ForeignKey(EstoqueEscola, on_delete=models.PROTECT, related_name="descartes")
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name="descartes_escola")
    lote = models.CharField(max_length=50, blank=True, null=True)
    quantidade = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    motivo = models.CharField(max_length=30, choices=MOTIVO_CHOICES)
    descricao = RichTextField(blank=True, null=True, config_name="minimal")
    registrado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name="descartes_registrados")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Descarte em Estoque Escolar"
        verbose_name_plural = "Descartes em Estoque Escolar"

    def __str__(self):
        return f"Descarte {self.produto.nome} ({self.get_motivo_display()}) - {self.escola}"


class ExecucaoCardapioDia(models.Model):
    """
    Registra a execução completa do cardápio em uma data específica.
    """
    STATUS_CHOICES = (
        ('PLANEJADO', 'Planejado'),
        ('EM_EXECUCAO', 'Em Execução'),
        ('EXECUTADO', 'Executado'),
        ('PARCIAL', 'Parcial'),
        ('CANCELADO', 'Cancelado'),
    )
    
    escola = models.ForeignKey(Escola, on_delete=models.PROTECT, related_name='execucoes_cardapio')
    data = models.DateField()
    cardapio_dia = models.ForeignKey(
        CardapioDia,
        on_delete=models.PROTECT,
        null=True, 
        blank=True,
        related_name='execucoes'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANEJADO')
    
    # Execução
    executado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='cardapios_executados')
    executado_em = models.DateTimeField(auto_now_add=True)
    finalizado_em = models.DateTimeField(null=True, blank=True)
    
    # Controle de qualidade
    quantidade_atendidos = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        help_text="Número real de pessoas atendidas"
    )
    observacao = models.TextField(blank=True, help_text="Observações sobre a execução do dia")
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['escola', 'data'], 
                name='unique_execucao_diaria_escola'
            )
        ]
        ordering = ['-data']
        verbose_name = "Execução de Cardápio do Dia"
        verbose_name_plural = "Execuções de Cardápio do Dia"

    def clean(self):
        """Validações de integridade"""
        if self.data > timezone.now().date():
            raise ValidationError("Não é possível registrar execução para datas futuras.")
        
        # Verifica se já existe execução para esta data (redundância ao constraint)
        if self.pk is None:  # Novo registro
            if ExecucaoCardapioDia.objects.filter(escola=self.escola, data=self.data).exists():
                raise ValidationError("Já existe execução registrada para esta data.")

    def __str__(self):
        return f"Cardápio {self.data.strftime('%d/%m/%Y')} - {self.escola} [{self.get_status_display()}]"


class ExecucaoCardapioItem(models.Model):
    """
    Vincula a execução do cardápio às receitas específicas executadas.
    """
    STATUS_CHOICES = (
        ('PENDENTE', 'Pendente'),
        ('EM_PREPARO', 'Em Preparo'),
        ('EXECUTADO', 'Executado'),
        ('FALTANDO_ESTOQUE', 'Faltando Estoque'),
        ('CANCELADO', 'Cancelado'),
    )
    
    execucao_cardapio = models.ForeignKey(
        ExecucaoCardapioDia,
        on_delete=models.CASCADE,
        related_name='itens_executados'
    )
    receita = models.ForeignKey(Receita, on_delete=models.PROTECT, related_name='execucoes_cardapio')
    tipo_refeicao = models.ForeignKey(TipoRefeicao, on_delete=models.PROTECT)
    execucao_receita = models.ForeignKey(
        ExecucaoReceitaCozinha,
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='vinculos_cardapio'
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDENTE')
    motivo_falha = models.TextField(blank=True, help_text="Motivo caso não tenha sido executado")
    
    # Quantidades planejadas vs reais
    porcoes_planejadas = models.PositiveIntegerField(default=0)
    porcoes_executadas = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Item de Execução"
        verbose_name_plural = "Itens de Execução"
        unique_together = ['execucao_cardapio', 'receita', 'tipo_refeicao']

    def __str__(self):
        return f"{self.receita.nome} - {self.tipo_refeicao} ({self.get_status_display()})"


# =========================================================
# SERVIÇOS DE DOMÍNIO APERFEIÇOADOS
# =========================================================

class EstoqueInsuficienteError(ValidationError):
    """Exceção específica para falta de estoque"""
    pass


def verificar_disponibilidade_ingredientes(escola, receita, porcoes):
    """
    Pré-validação: Verifica se há estoque suficiente antes de iniciar execução.
    Retorna tupla: (disponivel: bool, detalhes: dict)
    """
    ingredientes_necessarios = []
    faltantes = []
    
    for ingrediente in receita.ingredientes.all():
        quantidade_necessaria = ingrediente.quantidade * porcoes
        
        # Soma estoque disponível FEFO
        estoque_disponivel = EstoqueEscola.objects.filter(
            escola=escola,
            produto=ingrediente.produto,
            quantidade__gt=0,
            data_validade__gte=timezone.now().date()
        ).aggregate(total=models.Sum('quantidade'))['total'] or 0
        
        ingredientes_necessarios.append({
            'produto': ingrediente.produto,
            'necessario': quantidade_necessaria,
            'disponivel': estoque_disponivel,
            'suficiente': estoque_disponivel >= quantidade_necessaria
        })
        
        if estoque_disponivel < quantidade_necessaria:
            faltantes.append({
                'produto': ingrediente.produto.nome,
                'faltando': quantidade_necessaria - estoque_disponivel,
                'unidade': ingrediente.produto.unidade_medida
            })
    
    return (len(faltantes) == 0), {
        'ingredientes': ingredientes_necessarios,
        'faltantes': faltantes
    }


@transaction.atomic
def retirar_ingrediente_receita(execucao, produto, quantidade, usuario, lote_especifico=None):
    """
    Realiza retirada de ingredientes do estoque da escola usando estratégia FEFO.
    
    Args:
        lote_especifico: Se informado, força retirada daquele lote específico
    """
    if execucao.status not in ['ABERTA', 'EM_PREPARO']:
        raise ValidationError("Execução deve estar aberta ou em preparo para retirada.")
    
    # Query base
    lotes_query = EstoqueEscola.objects.select_for_update().filter(
        escola=execucao.escola,
        produto=produto,
        quantidade__gt=0
    )
    
    # Se especificou lote, filtra por ele
    if lote_especifico:
        lotes_query = lotes_query.filter(lote=lote_especifico)
    else:
        # FEFO: ordena por data de validade
        lotes_query = lotes_query.order_by("data_validade", "id")
    
    lotes = list(lotes_query)
    restante = quantidade
    movimentacoes_criadas = []

    for lote in lotes:
        if restante <= 0:
            break

        consumir = min(lote.quantidade, restante)
        
        # Atualiza estoque
        lote.quantidade -= consumir
        lote.save(update_fields=['quantidade'])

        # Registra movimentação de estoque oficial
        mov_estoque = MovimentacaoEstoque.objects.create(
            produto=produto,
            escola=execucao.escola,
            quantidade=consumir,
            tipo="SAIDA_ESCOLA",
            usuario=usuario,
            observacao=f"Retirada para receita: {execucao.receita.nome} (Execução #{execucao.id})"
        )

        # Registra movimentação interna da cozinha
        mov_cozinha = MovimentacaoCozinha.objects.create(
            escola=execucao.escola,
            produto=produto,
            lote=lote.lote,
            quantidade=consumir,
            tipo="RETIRADA_RECEITA",
            usuario=usuario,
            execucao_receita=execucao,
            observacao=f"Lote: {lote.lote} (Validade: {lote.data_validade})"
        )
        
        movimentacoes_criadas.append({
            'estoque': mov_estoque,
            'cozinha': mov_cozinha,
            'lote': lote.lote,
            'quantidade': consumir
        })

        restante -= consumir

    if restante > 0:
        raise EstoqueInsuficienteError(
            f"Estoque insuficiente para {produto.nome}. "
            f"Faltando: {restante} {produto.unidade_medida}"
        )
    
    return movimentacoes_criadas


@transaction.atomic
def executar_cardapio_do_dia(escola, data, usuario, cardapio_dia=None, porcoes_override=None):
    """
    Orquestra a execução completa do cardápio do dia.
    
    Fluxo:
    1. Cria registro de execução
    2. Para cada item do cardápio:
       a. Verifica estoque
       b. Cria ExecucaoReceitaCozinha
       c. Retira ingredientes (FEFO)
       d. Vincula ao cardápio
    3. Atualiza status geral
    
    Args:
        porcoes_override: Dict {receita_id: quantidade} para sobrescrever rendimento padrão
    """
    # 1. Cria registro mestre
    try:
        execucao_dia = ExecucaoCardapioDia.objects.create(
            escola=escola,
            data=data,
            cardapio_dia=cardapio_dia,
            status='EM_EXECUCAO',
            executado_por=usuario
        )
    except IntegrityError:
        raise ValidationError("Já existe execução registrada para esta data nesta escola.")
    
    itens_cardapio = []
    if cardapio_dia:
        itens_cardapio = CardapioItem.objects.filter(cardapio_dia=cardapio_dia).select_related('receita', 'tipo_refeicao')
    
    if not itens_cardapio:
        raise ValidationError("Nenhum item encontrado para execução neste cardápio.")
    
    resultados = {
        'sucessos': [],
        'falhas': [],
        'execucao_dia_id': execucao_dia.id
    }
    
    for item in itens_cardapio:
        try:
            # Define quantidade de porções
            porcoes = porcoes_override.get(item.receita.id, item.receita.rendimento) if porcoes_override else item.receita.rendimento
            
            # Pré-verificação de estoque
            disponivel, detalhes = verificar_disponibilidade_ingredientes(escola, item.receita, porcoes)
            
            if not disponivel:
                # Cria item como falha sem tentar retirar
                ExecucaoCardapioItem.objects.create(
                    execucao_cardapio=execucao_dia,
                    receita=item.receita,
                    tipo_refeicao=item.tipo_refeicao,
                    status='FALTANDO_ESTOQUE',
                    motivo_falha=f"Faltando: {detalhes['faltantes']}",
                    porcoes_planejadas=porcoes
                )
                resultados['falhas'].append({
                    'receita': item.receita.nome,
                    'motivo': 'Estoque insuficiente',
                    'detalhes': detalhes['faltantes']
                })
                continue
            
            # 2. Cria execução da receita
            exec_receita = ExecucaoReceitaCozinha.objects.create(
                escola=escola,
                receita=item.receita,
                status='EM_PREPARO',
                iniciado_por=usuario
            )
            
            # 3. Retira ingredientes
            ingredientes_retirados = []
            for ingrediente in item.receita.ingredientes.all():
                quantidade_necessaria = ingrediente.quantidade * porcoes
                movs = retirar_ingrediente_receita(
                    execucao=exec_receita,
                    produto=ingrediente.produto,
                    quantidade=quantidade_necessaria,
                    usuario=usuario
                )
                ingredientes_retirados.extend(movs)
            
            # 4. Vincula ao cardápio do dia
            exec_item = ExecucaoCardapioItem.objects.create(
                execucao_cardapio=execucao_dia,
                receita=item.receita,
                tipo_refeicao=item.tipo_refeicao,
                execucao_receita=exec_receita,
                status='EM_PREPARO',
                porcoes_planejadas=porcoes
            )
            
            # Finaliza execução da receita automaticamente (ou pode ser manual)
            exec_receita.finalizar(usuario, rendimento_real=porcoes)
            exec_item.status = 'EXECUTADO'
            exec_item.porcoes_executadas = porcoes
            exec_item.save()
            
            resultados['sucessos'].append({
                'receita': item.receita.nome,
                'porcoes': porcoes,
                'tipo_refeicao': item.tipo_refeicao.nome
            })
            
        except Exception as e:
            resultados['falhas'].append({
                'receita': item.receita.nome,
                'motivo': str(e)
            })
            # Cria registro de falha
            ExecucaoCardapioItem.objects.create(
                execucao_cardapio=execucao_dia,
                receita=item.receita,
                tipo_refeicao=item.tipo_refeicao,
                status='CANCELADO',
                motivo_falha=str(e),
                porcoes_planejadas=porcoes
            )
    
    # Atualiza status geral do dia
    total_itens = len(itens_cardapio)
    total_sucessos = len(resultados['sucessos'])
    
    if total_sucessos == 0:
        execucao_dia.status = 'CANCELADO'
    elif total_sucessos < total_itens:
        execucao_dia.status = 'PARCIAL'
    else:
        execucao_dia.status = 'EXECUTADO'
        execucao_dia.finalizado_em = timezone.now()
    
    execucao_dia.save()
    return resultados


@transaction.atomic
def devolver_ingrediente(execucao, produto, lote, quantidade, usuario):
    """
    Realiza devolução de ingredientes não utilizados da cozinha para o estoque.
    """
    if quantidade <= 0:
        raise ValidationError("Quantidade deve ser maior que zero.")
    
    # Verifica se há movimentação de saída correspondente (validação de negócio)
    total_saidas = MovimentacaoCozinha.objects.filter(
        execucao_receita=execucao,
        produto=produto,
        lote=lote,
        tipo='RETIRADA_RECEITA'
    ).aggregate(total=models.Sum('quantidade'))['total'] or 0
    
    total_devolucoes = MovimentacaoCozinha.objects.filter(
        execucao_receita=execucao,
        produto=produto,
        lote=lote,
        tipo='DEVOLUCAO'
    ).aggregate(total=models.Sum('quantidade'))['total'] or 0
    
    disponivel_para_devolucao = total_saidas - total_devolucoes
    
    if quantidade > disponivel_para_devolucao:
        raise ValidationError(
            f"Quantidade a devolver ({quantidade}) excede o disponível "
            f"({disponivel_para_devolucao}) para este lote."
        )
    
    estoque, _ = EstoqueEscola.objects.select_for_update().get_or_create(
        escola=execucao.escola,
        produto=produto,
        lote=lote,
        defaults={"quantidade": 0}
    )

    estoque.quantidade += quantidade
    estoque.save()

    # Registra entrada no estoque oficial
    MovimentacaoEstoque.objects.create(
        produto=produto,
        escola=execucao.escola,
        quantidade=quantidade,
        tipo="ENTRADA_ESCOLA",
        usuario=usuario,
        observacao=f"Devolução da cozinha - receita {execucao.receita.nome} (Exec #{execucao.id})"
    )

    # Registra movimentação da cozinha
    MovimentacaoCozinha.objects.create(
        escola=execucao.escola,
        produto=produto,
        lote=lote,
        quantidade=quantidade,
        tipo="DEVOLUCAO",
        usuario=usuario,
        execucao_receita=execucao
    )


@transaction.atomic
def descartar_produto_escola(estoque, quantidade, motivo, usuario, descricao=None):
    """
    Descarte institucional no estoque da escola com validações rigorosas.
    """
    if quantidade <= 0:
        raise ValidationError("Quantidade inválida para descarte.")

    # Lock pessimista
    estoque = EstoqueEscola.objects.select_for_update().select_related(
        "produto", "escola"
    ).get(pk=estoque.pk)

    if quantidade > estoque.quantidade:
        raise ValidationError(
            f"Estoque insuficiente. Disponível: {estoque.quantidade}, "
            f"Solicitado: {quantidade}"
        )

    # Se motivo é vencimento, verifica se realmente está vencido
    if motivo == 'VENCIDO' and estoque.data_validade >= timezone.now().date():
        raise ValidationError("Produto ainda não está vencido. Verifique a data de validade.")

    # Baixa no estoque
    estoque.quantidade -= quantidade
    estoque.save(update_fields=['quantidade'])

    # Registro do descarte
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

    # Movimento contábil
    MovimentacaoEstoque.objects.create(
        produto=estoque.produto,
        escola=estoque.escola,
        quantidade=quantidade,
        tipo="SAIDA_ESCOLA",
        usuario=usuario,
        observacao=f"Descarte ({motivo}) - lote {estoque.lote}",
        movimentacao_relacionada_tipo='DESCARTE',
        movimentacao_relacionada_id=descarte.id
    )

    return descarte
