from django.urls import path
from gestao_escolar.views.GE_pasta_escola import *
from gestao_escolar.views.pasta_session import *
from gestao_escolar.views import *
from gestao_escolar.views.views import   Pagina_inicio
#from dal import autocomplete

app_name = "Gestao_Escolar"

urlpatterns = [
    path('gestao_escolar', ListView_Escola.as_view(), name="GE_inicio"),    
    path('escolas/selecionar/<int:pk>/', Seleciona_escola, name='escola-selecionar'),
    path('gestao_escolar/anoLetivo', Seleciona_anoLetivo.as_view(), name="GE_anoLetivo"),
    path('anoLetivo/selecionar/<int:pk>/', seleciona_anoLetivo_session, name='selecionar-ano'),

    
    # A parti daqui o desenvolvimento da escola inicia
    path('gestao_escolar/Escola/', Pagina_inicio.as_view(), name="GE_Escola_inicio"),
    
    # Dados escola
    path('gestao_escolar/Escola/Create', CreateEscola.as_view(), name="CreateEscola"),
    path('gestao_escolar/Escola/Dados/Update/<int:pk>', UpdateEscolaDados.as_view(), name="UPdateEscolaDados"),
    path('gestao_escolar/Escola/<int:pk>', UpdateEscola.as_view(), name="DadosEscola"),

    # Turmas
    path('gestao_escolar/Turmas/', Create_turmas.as_view(), name="GE_Escola_turmas"),
    path('gestao_escolar/Turmas/all', ListView_Escola.as_view(), name="GE_Escola_turmas_lista"),
    path('gestao_escolar/Turmas/atualiza/<int:pk>', UpdateTurmas.as_view(), name="GE_Escola_Turmas_update"),    
    path('gestao_escolar/Turmas/delete/<int:pk>', Delete_Turmas.as_view(), name="GE_Escola_Turmas_delete"),

    # Alunos
    path('gestao_escolar/Alunos/', Create_Alunos.as_view(), name="GE_Escola_alunos_create"),
    path('gestao_escolar/Alunos/encontred/<str:nome_completo>/<str:nome_mae>', AlunosEcontred.as_view(), name="alunos_encontred"),
    path('gestao_escolar/Alunos/econtred', CreateAlunosConfirma.as_view(), name="alunos_create_encontred"),
    path('gestao_escolar/Alunos/etapa_2/<int:pk>', CreateAlunosConfirmaEtapa2.as_view(), name="alunos_create_etapa2"),    
    path('gestao_escolar/Alunos/etapa_3/<int:pk>', CreateAlunosConfirmaEtapa3.as_view(), name="alunos_create_etapa3"),
    path('gestao_escolar/Alunos/etapa_4/<int:pk>', CreateAlunosConfirmaEtapa4.as_view(), name="alunos_create_etapa4"),
    path('gestao_escolar/Alunos/etapa_5/<int:pk>', CreateAlunosConfirmaEtapa5.as_view(), name="alunos_create_etapa5"),
    path('gestao_escolar/Alunos/perfil/<int:pk>', PerfilAluno.as_view(), name="alunos_perfil"),


    path('gestao_escolar/Alunos/<int:pk>', Create_Alunos_Document.as_view(), name="GE_alunos_create_document"),     
    path('gestao_escolar/Alunos/documentos/atualiza<int:pk>', Update_Alunos_Document.as_view(), name="GE_alunos_update_document"),
    path('gestao_escolar/Alunos/atualiza/<int:pk>', Update_Alunos.as_view(), name="GE_Escola_alunos_update"),    
    path('gestao_escolar/Alunos/delete/<int:pk>', Delete_Alunos.as_view(), name="GE_Escola_alunos_delete"),
    #path('autocomplete/', autocomplete.Select2ListView.as_view(), name='autocomplete_aluno'),
   

    # Matriculas
    path('gestao_escolar/Matricula/all_classes', View_turmas_Matriculas.as_view(), name="GE_Escola_Matricula_Turmas_lista"), 
    path('gestao_escolar/Matricula/create/<int:pk>', Create_Matriculas.as_view(), name="GE_Escola_Matricula_create"),  
    path('gestao_escolar/Matricula/create/<int:pk>', Create_Matriculas.as_view(), name="GE_Escola_Matricula_create"),      
    path('gestao_escolar/Matricula/all', List_Matriculas.as_view(), name="GE_Escola_Matricula_lista"),
    path('gestao_escolar/Matricula/imprime/<int:pk>', ViewDetailMatriculasTurma.as_view(), name="Matricula_turma"),    
    path('gestao_escolar/Matricula/comprovante/imprime/<int:pk>', ComprovanteMatricula.as_view(), name="Matricula_comprovante"),    

    # Matriculas retorno aluno
    path('gestao_escolar/Matricula/create/aluno/<int:pk>', Create_Matriculas_Retorno_alunos.as_view(), name="GE_Escola_Matricula_create_aluno"),    
    path('gestao_escolar/Matricula/atualiza/<int:pk>', Update_Matricula.as_view(), name="GE_Escola_Matricula_update"),    
    path('gestao_escolar/Matricula/delete/<int:pk>', Delete_Matriculas.as_view(), name="GE_Escola_Matricula_delete"),

    # Remanejamento
    path('gestao_escolar/Matricula/remaneja_aluno/<int:pk>', Create_Remanejamento.as_view(), name="GE_Escola_Remaneja_create"),     
    path('gestao_escolar/Matricula/remaneja_aluno/Turma/<int:pk>', Update_Matricula_remanejamento.as_view(), name="GE_Escola_Remaneja_update"),     
    #path('gestao_escolar/Matricula/remaneja_aluno/Turma/<int:pk>', Update_Matricula_remanejamento.as_view(), name="GE_Escola_Remaneja_update"), 

    # Discplinas
    path('gestao_escolar/Disciplinas/create/', Create_disciplinas.as_view(), name="GE_Disciplina_create"),     
    path('gestao_escolar/Matricula/remaneja_aluno/Turma/<int:pk>', Update_Matricula_remanejamento.as_view(), name="GE_Escola_Remaneja_update"), 

    # Grades
    path('gestao_escolar/Grades/create/turmas', View_turmas_Grade.as_view(), name="Grades_turmas"),   
    path('gestao_escolar/Grades/create/<int:pk>', Create_Grades.as_view(), name="Grades_create"),   
    path('gestao_escolar/Grades/update/<int:pk>', Update_Grade.as_view(), name="Grades_update"),     
    path('gestao_escolar/Grades/delete/<int:pk>', Delete_Grade.as_view(), name="Grades_delete"),  
    path('gestao_escolar/Matricula/remaneja_aluno/Turma/<int:pk>', Update_Matricula_remanejamento.as_view(), name="GE_Escola_Remaneja_update"),    

    # Professores
    path('gestao_escolar/Professores/Pessoas', Create_Pessoa_Professores.as_view(), name="Professores_Pessoa_create"),   
    path('gestao_escolar/Professores/Pessoas/vinculo/<int:pk>', Create_Pessoa_Vinculo.as_view(), name="Professores_Pessoa_vinculo_create"), 
    path('gestao_escolar/Professores/Pessoas/vinculo/aplica/<int:pk>,<slug:vinculo>,<int:ano>', Create_Pessoa_Aplica_Vinculo.as_view(), name="Professores_Pessoa_aplica_vinculo_create"),     
    path('gestao_escolar/Professores/Pessoas/encaminhamento/<int:pk>,<int:destino>,<int:profissao>', Create_Pessoa_Encaminhamento.as_view(), name="Professores_Encaminhamento"), 
    path('gestao_escolar/Professores/', Create_Professores.as_view(), name="GE_Professores_create"),    
    path('gestao_escolar/Professores/encaminhamento/<int:pk>', EncaminhaEscola.as_view(), name="encaminha_escola"),   
    path('gestao_escolar/Professores/encaminhamento/apagar/<int:pk>', EncaminhaEscolaDelete.as_view(), name="encaminha_escolaDelete"),   

    # pessoas (para uso de decreto e outros) ----------------------------------------------
    #path('pessoas/', PessoasListView.as_view(), name='pessoas-list'),
    #path('pessoas/<int:pk>/', PessoasDetailView.as_view(), name='pessoas-detail'),
    path('pessoas/criar/', PessoasCreateView.as_view(), name='pessoas-create'),
    path('pessoas/<int:pk>/editar/', PessoasUpdateView.as_view(), name='pessoas-update'),
    path('pessoas/<int:pk>/excluir/', PessoasDeleteView.as_view(), name='pessoas-delete'),

    # pessoasContrato (para uso de decreto e outros) ----------------------------------------------
    path('pessoas/contrato/<int:pk>', PessoasContratoCreateView.as_view(), name='pessoasContrato-create'),

    # Decretos
    #path('decretos/', DecretoListView.as_view(), name='decreto-list'),
    #path('decretos/<int:pk>/', DecretoDetailView.as_view(), name='decreto-detail'),
    path('decretos/criar/', DecretoCreateView.as_view(), name='decreto-create'),
    path('decretos/<int:pk>/editar/', DecretoUpdateView.as_view(), name='decreto-update'),
    #path('decretos/<int:pk>/excluir/', DecretoDeleteView.as_view(), name='decreto-delete'),

    # Decreto Ativo    
    path('decretos/ano_ativo/<int:pk>', DecretoAnoLetivoAtivo_create.as_view(), name='decreto-ativo'),
    

    # Definir o cargo que o profissional irá exercer na escola
    path('gestao_escolar/Profissionais/', Create_Define_Profissional.as_view(), name="Professores_Profissionais_create"),      
    path('gestao_escolar/Profissionais/<int:pk>', Update_Define_Profissional.as_view(), name="Professores_Profissionais_atualiza"),  

    # Gestão de Turmas
    path('gestao_escolar/Gestao_Turmas/', GestaoSelecionaTurma.as_view(), name="NotasAluno_all_create"),  
    path('gestao_escolar/Gestao_Turmas/turma/<int:pk>', GerirTurmaSelecionada.as_view(), name="NotasAluno_one_create"),      
    path('gestao_escolar/Gestao_Turmas/turma/notas/<int:pk>', verifica_e_cria_gestao_turmas, name="NotasAluno"),        
    path('gestao_escolar/Gestao_Turmas/aluno/notas/<int:pk>',gestao_turmas_update_view, name='gestao_turmas_update'),  
    path('gestao_escolar/Gestao_Turmas/aluno/conselhoClasse/<int:pk>',AprovaConselho.as_view(), name='aprovaConselho'),  

    # Plano de Aula
    path('relatorio/plano/<int:plano_id>/', relatorio_plano_aula_frequencia, name='relatorio_plano_aula'),

    # GErar horario
    path('horario/validade/<int:turma_id>/', CriaValidadeHorario.as_view(), name='validadeHorario'),
    path('horario/validade/update/<int:pk>/', CriaValidadeHorarioUpdate.as_view(), name='validadeHorarioUpdate'),
    path('horario/add/<int:turma_id>/', alocar_aulas, name='criar_horario'),
    path('horario/edit/<int:turma_id>/', visualizaHorarioTuram, name='edit_horario'),
    path('horario/<int:pk>/turma/<int:turma_id>/update/', HorarioUpdateView.as_view(), name='horario_update'),
    

    # Notas Trimestre
    path('criar-gestao-turma/notas/trimestre/<int:aluno_id>/', GestaoTurmasNotas.as_view(), name='criar_gestao_turma'), 
    path('gestao_turmas/<int:aluno_id>/<int:trimestre_id>/', create_or_update_gestao_turmas, name='create_or_update_gestao_turmas'),
    path('gestao_turmas/recuperaFinal/<int:aluno_id>/<int:trimestre_id>/', create_or_update_gestao_turmas_recupera, name='recuperaFinal'),
    path('gestao_turmas/media/<int:aluno_id>/', create_or_update_Media_turmas, name='create_or_update_media_turmas'),
    
    # Notas Trimestre
    path('criar-gestao-turma/parecer/<int:turma_id>/', gestao_turmas_parecer, name='criaParecer'), 
    path('criar-gestao-turma/parecer/aluno/<int:pk>/<int:trimestre>/', alunoGestaoTurmasParecer, name='criaParecerAluno'), 
    path('criar-gestao-turma/parecer/aluno/Final<int:pk>/<int:trimestre>/', alunoGestaoTurmasParecerResumo, name='criaParecerAlunoFinal'), 
    
    # IMPRESSOS
    path('turmas/impressao', Imprime_Turmas.as_view(), name='imprime_list_turmas'),
    path('turmas/impressao/filtros', ImprimeTurmasFiltros.as_view(), name='imprime_turmas_filtros'),
    path('escolas/impressao', Imprime_Escolas.as_view(), name='imprime_list_escolas'),
    path('horarios/all/impressao', ImprimeAllHorarios .as_view(), name='imprime_all_horarios'),
    
    path('historico/<int:pk>/', HistoricoEscolarAlunoView.as_view(), name='historico_escolar'),


    # Ferramentas
    # path('image-to-doc/', Image_to_doc, name='image_to_doc'),

    # QR_code
    path('gestao_escolar/Criar_Qrcode/', Create_QrCode, name="GE_QrCode"),       

    # Bairro   
    path('cidade/bairro/novo/', BairroCreateView.as_view(), name='bairro-create'),
    path('cidade/bairro/<int:pk>/editar/', BairroUpdateView.as_view(), name='bairro-update'),
    path('cidade/bairro/<int:pk>/deletar/', BairroDeleteView.as_view(), name='bairro-delete'),

    # Bairro   
    path('cidade/novo/', CidadeCreateView.as_view(), name='cidade-create'),
    path('cidade/<int:pk>/editar/', CidadeUpdateView.as_view(), name='cidade-update'),
    path('cidade/<int:pk>/deletar/', CidadeDeleteView.as_view(), name='cidade-delete'),

    path('resumo/<int:pk>/', atualizarResumoFinal, name='resumo'),
    

    # Feriados
    path('calendario/<int:ano>/<int:mes>/', calendario_mes, name='calendario_mes'),
    path('calendario/', calendario_mes, {'ano': datetime.now().year, 'mes': datetime.now().month}, name='calendario_mes_atual'),

    # Matricula Online - Area Publica
    path('matricula_online/', pesquisar_aluno, name='pesquisar_aluno'),
    path('cadastro_aluno/<str:nome>/<str:mae>/<str:cpf>', cadastro_aluno_etapa1, name='cadastro_aluno_etapa1'),
    path('cadastro_aluno/exibe/dados/acesso/<int:aluno_id>', cadastro_aluno_etapa1_exibeSenha, name='cadastro_aluno_etapa1_exibeSenha'),    
    path('cadastro_aluno/etapa2/documentos/endereco/<int:aluno_id>', cadastro_aluno_etapa2, name='cadastro_aluno_etapa2'),
    path('cadastro_aluno/etapa3/<int:aluno_id>', cadastro_aluno_etapa3, name='cadastro_aluno_etapa3'),
    path('cadastro_aluno/certidao/<int:aluno_id>', cadastro_aluno_etapa4, name='cadastro_aluno_etapa4'),
    path('cadastro_aluno/fisicoEsaude/<int:aluno_id>', cadastro_aluno_etapa5, name='cadastro_aluno_etapa5'),


    # Escola Matricula Online
    # URLs para EscolaMatriculaOnline
    path('escolas/adicionar/', adicionar_escola, name='adicionar_escola'),
    path('escolas/editar/<int:pk>/', editar_escola, name='editar_escola'),
    path('escolas/deletar/<int:pk>/', deletar_escola, name='deletar_escola'),

    # URLs para SerieOnline
    path('series/adicionar/<int:pk>', adicionar_serie, name='adicionar_serie'),
    path('series/editar/<int:pk>/', editar_serie, name='editar_serie'),
    path('series/deletar/<int:pk>/', deletar_serie, name='deletar_serie'),

    # Faze de matricula online do aluno
    path('matricula_online/<int:aluno_id>/', matricular_aluno, name='matricular_aluno'),
    path('matricula_online/<int:aluno_id>/<int:serie_id>/', finaliza_matricular_aluno, name='matricular_alunoSerie'),
    path('matricula_online/impugna/<int:mat_id>', matricula_confirma_impugna, name='matricular_confirma_impugna'),
    path('matricula_online/impugna/confirmada/<int:mat_id>', matricula_confirmada, name='matricularOnine_confirma'),

    
    # Apuração final
    path('apuracaoFinal/selecionaTurma/', listaTurmaApuracao, name='apuracaoSelecTurma'),
    path('apuracaoFinal/selecionaTurma/<int:turma_id>', selecionaTurmaSelecionada, name='apuracaoSelec'),

    


    
    
] 


urlpatterns.append(path('gestao_escolar/Pessoas/Criar/', Create_Pessoa_Professores.as_view(), name="GE_Create_Professores"))

"""

from django.db import connection
from django.urls import path
from .views import Create_Pessoa_Professores

try:
    def config_plataforma_table_exists():
        return 'rh_config_plataforma' in connection.introspection.table_names()

    if config_plataforma_table_exists():
        if Config_plataforma.objects.exists():
            config = Config_plataforma.objects.first()
            if config.rh_Ativo:
                urlpatterns.append(path('gestao_escolar/Pessoas/Criar/', Create_Pessoa_Professores.as_view(), name="GE_Create_Professores"))
            else:
                urlpatterns.append(path('gestao_escolar/Pessoas/Criar/', Create_Pessoa_Professores.as_view(), name="GE_Create_Professores"))
        else:
            urlpatterns.append(path('gestao_escolar/Pessoas/Criar/', Create_Pessoa_Professores.as_view(), name="GE_Create_Professores"))
    else:
        urlpatterns.append(path('gestao_escolar/Pessoas/Criar/', Create_Pessoa_Professores.as_view(), name="GE_Create_Professores"))
except Exception as e:
"""
