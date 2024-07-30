import subprocess
import sys
import time

def run_command(command):
    """Executa um comando no sistema e retorna o código de saída e a saída padrão."""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return process.returncode, stdout.decode(), stderr.decode()

def check_migrations():
    """Verifica se há migrações pendentes e alterna entre makemigrations e migrate."""
    while True:
        # Executa makemigrations
        print("Executando makemigrations...")
        returncode, stdout, stderr = run_command("python manage.py makemigrations")
        print(stdout)
        if returncode != 0:
            print(f"Erro ao executar makemigrations: {stderr}")
            sys.exit(1)
        
        if "No changes detected" in stdout:
            # Se não há alterações detectadas, execute migrate
            print("Nenhuma mudança detectada. Executando migrate...")
            returncode, stdout, stderr = run_command("python manage.py migrate")
            print(stdout)
            if returncode != 0:
                print(f"Erro ao executar migrate: {stderr}")
                sys.exit(1)
            break  # Saia do loop se não houver novas migrações a aplicar
        
        # Se houve novas migrações, aguarde um curto período antes de tentar novamente
        print("Alterações detectadas. Tentando novamente em breve...")
        time.sleep(2)

if __name__ == "__main__":
    check_migrations()
