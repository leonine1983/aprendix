import subprocess
import sys
import time
from datetime import datetime

# Usa o mesmo interpretador Python que executa este script
PYTHON_CMD = sys.executable

APPS = [
    # 🔹 Meus apps
    'rh',   
    'admin_acessos',     
    'gestao_escolar',  
    'docsGestao_Escolar',  
    'modulo_aluno',
    'modulo_professor',
    'modulo_atividadesPedagogicas',
    
    # 🔹 Base institucional
    'core', # Nota: É mais seguro usar 'core' do que 'core.apps.CoreConfig' no CLI

    # 🔹 Domínio Merenda
    "merendaEscolar",

    # 🔹 Módulos dependentes
    "modulo_Merendeiras",
    "modulo_coordenacao",    
    
    # 🔹 Apps de terceiros (Geralmente não precisam de makemigrations, mas o script lida com isso)
    'ckeditor',
    'ckeditor_uploader',    
    'widget_tweaks',
    'django.contrib.humanize',
    "django_extensions",
    "arquitetura"
]

LOG_FILE = "migracoes.log"
DEBUG_MODE = True  # Se True, imprime TODA a saída do Django. Se False, imprime apenas resumos.


def log(message, end="\n", level="INFO"):
    """Função de log unificada para console e arquivo."""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    
    # Adiciona um prefixo visual baseado no nível
    prefixes = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "START": "▶️",
        "END": "🏁"
    }
    prefix = prefixes.get(level, "•")
    
    full_message = f"{timestamp} {prefix} {message}"
    print(full_message, end=end)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        # Remove emojis do arquivo de log para manter compatibilidade/limpeza, opcional
        clean_message = full_message # Ou use regex para remover emojis se preferir
        f.write(clean_message + end)


def run_command(command):
    """Executa comando e retorna código, stdout e stderr."""
    process = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    return process.returncode, process.stdout.strip(), process.stderr.strip()


# ---------------------------------------------------------
# ETAPA 1 — MIGRAÇÃO GLOBAL
# ---------------------------------------------------------
def migrate_global():
    log("=" * 60, level="INFO")
    log("ETAPA 1 — MIGRAÇÃO GLOBAL DO DJANGO", level="START")
    log("=" * 60, level="INFO")

    log("Executando: makemigrations (global)")
    retcode, stdout, stderr = run_command(f"{PYTHON_CMD} manage.py makemigrations")

    if retcode != 0:
        log(f"FALHA CRÍTICA no makemigrations global:\n{stderr}", level="ERROR")
        sys.exit(1)
    
    if DEBUG_MODE or "No changes detected" not in stdout and "Nenhuma alteração" not in stdout:
        log(stdout or "[sem saída]", level="INFO")

    log("Executando: migrate (global)")
    retcode, stdout, stderr = run_command(f"{PYTHON_CMD} manage.py migrate")

    if retcode != 0:
        log(f"FALHA CRÍTICA no migrate global:\n{stderr}", level="ERROR")
        sys.exit(1)
    
    if DEBUG_MODE:
        log(stdout or "[sem saída]", level="INFO")

    log("Migração global concluída com sucesso.", level="SUCCESS")
    log("-" * 60 + "\n")


# ---------------------------------------------------------
# ETAPA 2 — MIGRAÇÃO APP POR APP (COM DEBUG DETALHADO)
# ---------------------------------------------------------
def migrate_app(app_name, index):
    log("=" * 60, level="INFO")
    log(f"INICIANDO MIGRAÇÃO: [{index:02d}/{len(APPS):02d}] {app_name}", level="START")
    log("=" * 60, level="INFO")

    app_start_time = time.time()

    # 1. Makemigrations
    log(f"Gerando migrações para '{app_name}'...", level="INFO")
    make_start = time.time()
    retcode, stdout, stderr = run_command(f"{PYTHON_CMD} manage.py makemigrations {app_name}")
    make_duration = time.time() - make_start

    if retcode != 0:
        log(f"FALHA em makemigrations ({app_name}) - {make_duration:.2f}s", level="ERROR")
        log(f"Detalhe do erro:\n{stderr}", level="ERROR")
        sys.exit(1)

    # Análise inteligente da saída do makemigrations
    if "No changes detected" in stdout or "Nenhuma alteração detectada" in stdout:
        log(f"Nenhuma alteração de modelo detectada para '{app_name}'.", level="WARNING")
    else:
        log(f"Migrações geradas com sucesso ({make_duration:.2f}s).", level="SUCCESS")
        if DEBUG_MODE and stdout:
            log(f"Saída: {stdout}", level="INFO")

    # 2. Migrate
    log(f"Aplicando migrações no banco para '{app_name}'...", level="INFO")
    mig_start = time.time()
    retcode, stdout, stderr = run_command(f"{PYTHON_CMD} manage.py migrate {app_name}")
    mig_duration = time.time() - mig_start

    if retcode != 0:
        log(f"FALHA em migrate ({app_name}) - {mig_duration:.2f}s", level="ERROR")
        log(f"Detalhe do erro:\n{stderr}", level="ERROR")
        sys.exit(1)

    log(f"Migrações aplicadas com sucesso ({mig_duration:.2f}s).", level="SUCCESS")
    if DEBUG_MODE and stdout:
        # Filtra apenas as linhas relevantes de aplicação para não poluir demais
        relevant_output = [line for line in stdout.split('\n') if 'Applying' in line or 'App' in line]
        if relevant_output:
            log("Detalhes da aplicação:\n" + "\n".join(relevant_output), level="INFO")

    # Resumo Final do App
    app_total_duration = time.time() - app_start_time
    log("-" * 60, level="INFO")
    log(f"CONCLUÍDO: {app_name}", level="END")
    log(f"Tempo Total: {app_total_duration:.2f}s (Make: {make_duration:.2f}s | Migrate: {mig_duration:.2f}s)", level="INFO")
    log("-" * 60 + "\n")


def migrate_all_apps():
    log("=" * 60, level="INFO")
    log("ETAPA 2 — MIGRAÇÃO CONTROLADA POR APP", level="START")
    log("=" * 60, level="INFO")

    total_start = time.time()

    for index, app in enumerate(APPS, start=1):
        migrate_app(app, index)

    total_duration = time.time() - total_start

    log("=" * 60, level="INFO")
    log("TODAS AS MIGRAÇÕES DOS APPS CONCLUÍDAS COM SUCESSO", level="SUCCESS")
    log(f"Tempo total de processamento: {total_duration:.2f} segundos", level="INFO")
    log("=" * 60 + "\n")


# ---------------------------------------------------------
# ETAPA 3 — CRIAÇÃO DE SUPERUSUÁRIO
# ---------------------------------------------------------
def criar_superuser():
    log("Verificando/criando superusuário 'rogerio'...", level="INFO")

    # Script mais robusto e legível para o shell do Django
    shell_script = """
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='rogerio').exists():
    User.objects.create_superuser('rogerio', 'rogerio@example.com', 'Roger2016')
    print('CRIADO')
else:
    print('EXISTE')
"""
    command = f'{PYTHON_CMD} manage.py shell -c "{shell_script}"'
    retcode, stdout, stderr = run_command(command)

    if retcode == 0:
        if "CRIADO" in stdout:
            log("Superusuário 'rogerio' criado com sucesso.", level="SUCCESS")
        else:
            log("Superusuário 'rogerio' já existe. Nenhuma ação necessária.", level="WARNING")
    else:
        log(f"Falha ao verificar/criar superusuário:\n{stderr}", level="ERROR")


# ---------------------------------------------------------
# EXECUÇÃO PRINCIPAL
# ---------------------------------------------------------
if __name__ == "__main__":
    # Inicializa o arquivo de log (sobrescreve o anterior para começar limpo)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("==================================================\n")
        f.write("          LOG DE MIGRAÇÕES DJANGO                 \n")
        f.write(f"Início da execução: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("==================================================\n\n")

    try:
        migrate_global()
        migrate_all_apps()
        criar_superuser()
        
        log("🎉 PROCESSO FINALIZADO COM SUCESSO!", level="SUCCESS")
        
    except Exception as e:
        log(f"ERRO INESPERADO NO SCRIPT: {str(e)}", level="ERROR")
        sys.exit(1)