import subprocess
import sys
import time
import os
from datetime import datetime

# Lista dos apps a migrar
APPS = [
    "admin_acessos",
    "rh",
    "controle_estoque",
    "gestao_escolar",
    "docsGestao_Escolar",
    "modulo_professor",
    "modulo_aluno"
]

# Nome do arquivo de log
LOG_FILE = "migracoes.log"

def log(message, end="\n"):
    """Escreve a mensagem no terminal e no arquivo de log."""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full_message = f"{timestamp} {message}"
    print(full_message, end=end)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_message + end)

def run_command(command, env=None):
    """Executa um comando e retorna (código de saída, stdout, stderr)."""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    stdout, stderr = process.communicate()
    return process.returncode, stdout.decode().strip(), stderr.decode().strip()

def migrate_app_by_app():
    """Executa makemigrations e migrate por app, registrando log detalhado."""
    log("🚀 Iniciando processo de migração app por app...\n")

    for app in APPS:
        log(f"🔧 App: {app}")
        start_time = time.time()

        # makemigrations
        retcode, stdout, stderr = run_command(f"python manage.py makemigrations {app}")
        log(f"📄 makemigrations [{app}]:")
        log(stdout or "[sem saída]")
        if retcode != 0:
            log(f"❌ Erro em makemigrations para {app}: {stderr}")
            sys.exit(1)

        # migrate
        retcode, stdout, stderr = run_command(f"python manage.py migrate {app}")
        log(f"📦 migrate [{app}]:")
        log(stdout or "[sem saída]")
        if retcode != 0:
            log(f"❌ Erro em migrate para {app}: {stderr}")
            sys.exit(1)

        duration = time.time() - start_time
        log(f"✅ Concluído {app} em {duration:.2f} segundos.\n")

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

    migrate_app_by_app()
    criar_superuser()
