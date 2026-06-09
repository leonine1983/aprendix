import subprocess
import sys
import time
from datetime import datetime

# Usa o mesmo interpretador Python que executa este script
PYTHON_CMD = sys.executable

APPS = [
    # meus apps
    'rh',   
    'admin_acessos',     
    'gestao_escolar',  
    #'controle_estoque', 
    'docsGestao_Escolar',  
    'modulo_aluno',
    'modulo_professor',
    'modulo_atividadesPedagogicas',
    # 🔹 Base institucional
    'core.apps.CoreConfig',

    # 🔹 Domínio Merenda
    "merendaEscolar",

    # 🔹 Módulos dependentes
    "modulo_Merendeiras",
    "modulo_coordenacao",

    
    'ckeditor',
    'ckeditor_uploader',    
    'widget_tweaks',
    'django.contrib.humanize',
    "django_extensions",
    "arquitetura"
]

LOG_FILE = "migracoes.log"


def log(message, end="\n"):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full_message = f"{timestamp} {message}"
    print(full_message, end=end)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_message + end)


def run_command(command):
    process = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

    return process.returncode, process.stdout.strip(), process.stderr.strip()


# ---------------------------------------------------------
# ETAPA 1 — MIGRAÇÃO GLOBAL
# ---------------------------------------------------------

def migrate_global():

    log("================================================")
    log("🚀 ETAPA 1 — MIGRAÇÃO GLOBAL DO DJANGO")
    log("================================================\n")

    retcode, stdout, stderr = run_command(f"{PYTHON_CMD} manage.py makemigrations")

    log("📄 makemigrations GLOBAL:")
    log(stdout or "[sem saída]")

    if retcode != 0:
        log(f"❌ Erro no makemigrations global: {stderr}")
        sys.exit(1)

    retcode, stdout, stderr = run_command(f"{PYTHON_CMD} manage.py migrate")

    log("📦 migrate GLOBAL:")
    log(stdout or "[sem saída]")

    if retcode != 0:
        log(f"❌ Erro no migrate global: {stderr}")
        sys.exit(1)

    log("\n✅ Migração global concluída.\n")


# ---------------------------------------------------------
# ETAPA 2 — MIGRAÇÃO APP POR APP
# ---------------------------------------------------------

def migrate_app(app_name, index):

    log("------------------------------------------------")
    log(f"🔧 APP {index}/{len(APPS)} → {app_name}")
    log("------------------------------------------------")

    start_time = time.time()

    retcode, stdout, stderr = run_command(
        f"{PYTHON_CMD} manage.py makemigrations {app_name}"
    )

    log(f"📄 makemigrations [{app_name}]")
    log(stdout or "[sem saída]")

    if retcode != 0:
        log(f"❌ Erro em makemigrations: {stderr}")
        sys.exit(1)

    retcode, stdout, stderr = run_command(
        f"{PYTHON_CMD} manage.py migrate {app_name}"
    )

    log(f"📦 migrate [{app_name}]")
    log(stdout or "[sem saída]")

    if retcode != 0:
        log(f"❌ Erro em migrate: {stderr}")
        sys.exit(1)

    duration = time.time() - start_time

    log("\n🏁 FINALIZAÇÃO DO APP")
    log(f"📦 App........: {app_name}")
    log(f"⏱ Tempo......: {duration:.2f}s")
    log("------------------------------------------------\n")


def migrate_all_apps():

    log("================================================")
    log("🚀 ETAPA 2 — MIGRAÇÃO CONTROLADA POR APP")
    log("================================================\n")

    start = time.time()

    for index, app in enumerate(APPS, start=1):
        migrate_app(app, index)

    total = time.time() - start

    log("================================================")
    log("🎉 TODAS AS MIGRAÇÕES DOS APPS CONCLUÍDAS")
    log(f"⏱ Tempo total: {total:.2f} segundos")
    log("================================================\n")


# ---------------------------------------------------------
# ETAPA 3 — CRIAÇÃO DE SUPERUSUÁRIO
# ---------------------------------------------------------

def criar_superuser():

    log("👑 Verificando superusuário 'rogerio'")

    command = (
        f"{PYTHON_CMD} manage.py shell -c \""
        "from django.contrib.auth import get_user_model;"
        "User=get_user_model();"
        "User.objects.filter(username='rogerio').exists() or "
        "User.objects.create_superuser('rogerio','rogerio@example.com','Roger2016')"
        "\""
    )

    retcode, stdout, stderr = run_command(command)

    if retcode == 0:
        log("✅ Superusuário pronto.\n")
    else:
        log(f"⚠️ Erro ao criar superusuário: {stderr}\n")


# ---------------------------------------------------------
# EXECUÇÃO
# ---------------------------------------------------------

if __name__ == "__main__":

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("===== LOG DE MIGRAÇÕES DJANGO =====\n")
        f.write(f"Início: {datetime.now()}\n\n")

    migrate_global()
    migrate_all_apps()
    criar_superuser()