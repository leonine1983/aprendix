import subprocess
import sys
import time
import os
from datetime import datetime

# Ordem correta de migrações
APPS = [
    "rh",                 
    "admin_acessos",      
    "controle_estoque",
    "gestao_escolar",    
    "modulo_professor",
    "modulo_aluno",
    "docsGestao_Escolar",

    # 🔽 Adicionados conforme solicitado
    "core",
    "merendaEscolar",
    "modulo_Merendeiras",
    "modulo_coordenacao",
]

LOG_FILE = "migracoes.log"

def log(message, end="\n"):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full_message = f"{timestamp} {message}"
    print(full_message, end=end)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_message + end)

def run_command(command, env=None):
    """Executa um comando shell e retorna (retcode, stdout, stderr)."""
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    stdout, stderr = process.communicate()
    return process.returncode, stdout.decode().strip(), stderr.decode().strip()

def migrate_app(app_name):
    """Executa makemigrations e migrate para um app específico."""
    log(f"🔧 App: {app_name}")
    start_time = time.time()

    # makemigrations
    retcode, stdout, stderr = run_command(f"python manage.py makemigrations {app_name}")
    log(f"📄 makemigrations [{app_name}]:")
    log(stdout or "[sem saída]")
    if retcode != 0:
        log(f"❌ Erro em makemigrations para {app_name}: {stderr}")
        sys.exit(1)

    # migrate
    retcode, stdout, stderr = run_command(f"python manage.py migrate {app_name}")
    log(f"📦 migrate [{app_name}]:")
    if retcode != 0 and "InconsistentMigrationHistory" in stderr:
        log(f"⚠️ Inconsistência detectada, aplicando fake migrate para {app_name}")
        retcode, stdout, stderr = run_command(f"python manage.py migrate {app_name} --fake")

    log(stdout or "[sem saída]")
    if retcode != 0:
        log(f"❌ Erro final em migrate para {app_name}: {stderr}")
        sys.exit(1)

    duration = time.time() - start_time
    log(f"✅ Concluído {app_name} em {duration:.2f} segundos.\n")

def migrate_all_apps():
    log("🚀 Iniciando processo de migração app por app...\n")
    for app in APPS:
        migrate_app(app)
    log("🎉 Todas as migrações foram aplicadas com sucesso!\n")

def criar_superuser():
    log("👑 Criando superusuário 'rogerio'...")
    command = (
        "python manage.py shell -c \""
        "from django.contrib.auth import get_user_model; "
        "User = get_user_model(); "
        "User.objects.filter(username='rogerio').exists() or "
        "User.objects.create_superuser('rogerio', 'rogerio@example.com', 'Roger2016')"
        "\""
    )
    retcode, stdout, stderr = run_command(command)
    if retcode == 0:
        log("✅ Superusuário 'rogerio' criado com sucesso!\n")
    else:
        log(f"⚠️ Erro ao criar superusuário: {stderr}\n")

if __name__ == "__main__":
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("===== LOG DE MIGRAÇÕES DJANGO =====\n")
        f.write(f"Início: {datetime.now()}\n\n")

    migrate_all_apps()
    criar_superuser()