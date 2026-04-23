
from .views import *
# Estoque Central
from .entrada_central import *
from .estoqueCentral.registrarDescarteView import *
from .estoqueCentral.notaDescarteView import *
from .estoqueCentral.descarte_relatorio import *
from .estoqueCentral.descarteDetalhesView import *

# TRansferencias
from .transferencias.transferenciaEnviarView import *
from .transferencias.transferenciaReceberView import *
from .transferencias.transferenciaDetailView import *
from .transferencias.transferenciaListView import *
from .transferencias.transferenciaCreateView import *
from .transferencias.transferenciaPrintView import *


# Transferencia  Itens
from .transferenciaItens.transferenciaItemCreateView import *
from .transferenciaItens.transferenciaItemDeleteView import *
from .transferenciaItens.transferenciaItemUpdateView import *

# Confirma transferencia
from .escola_confirma_transferencia.notificacaoListView import *
from .escola_confirma_transferencia.listaEscolasRecebimentoView import *
from .escola_confirma_transferencia.transferenciasAbertasEscolaView import *
from .escola_confirma_transferencia.receberTransferenciaView import *
from .escola_confirma_transferencia.transferenciaConferenciaView import *
from .escola_confirma_transferencia.estoqueEscolaDashboardView import *
from .escola_confirma_transferencia.listaEscolasViewDashboard import *


# Receitas
from .receitas.receitaListView import *

# RELATÓRIOS
from .relatorios.relatorioEstoqueCentralView import *

from .cozinha.view import *

from .configuraPessoal.configuracaoPessoalUpdateView import *