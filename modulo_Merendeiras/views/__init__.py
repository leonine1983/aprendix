from .views import *
from .receberTransferenciaView import *
from .transferenciaConferenciaView import *


from .transferenciasRecebidasListView import *
from .transferenciaEscolaDetailView import *

# Cardapio Hoje
from .cardápioHoje.cardapioHojeView import CardapioHojeView
from .cardápioHoje.receitaDetailView import ReceitaDetailView

# Estoque Escola
from .estoque.estoqueEscolaListView import *

# Descarte
from .estoque.descartes.descartarEstoqueView import *
from .estoque.descartes.listar_descartes_view import *

# Movimentação de estoque
from .movimentacaoEstoque.movimentacaoEstoqueDetailView import *
from .movimentacaoEstoque.movimentacaoEstoqueListView import *

# cOZINHA
from .cozinha.painelExecucaoView import PainelExecucaoView