
## Instalando o PostgreSQL

```
# Nós fizemos isso acima
sudo apt install postgresql postgresql-contrib -y
```

Caso queira mais detalhes: https://youtu.be/VLpPLaGVJhI  
Mais avançado: https://youtu.be/FZaEukN_raA

### Configurações

```
sudo -u postgres psql
# Criando um super usuário
CREATE ROLE usuario WITH LOGIN SUPERUSER CREATEDB CREATEROLE PASSWORD 'senha';
# Criando a base de dados
CREATE DATABASE basededados WITH OWNER usuario;
# Dando permissões
GRANT ALL PRIVILEGES ON DATABASE basededados TO usuario;
# Saindo
\q
sudo systemctl restart postgresql
```

Caso queira mais detalhes: https://youtu.be/VLpPLaGVJhI  
Mais avançado: https://youtu.be/FZaEukN_raA

## Configurando o git

```
git config --global user.name 'Rogerio da Silva'
git config --global user.email 'rogerleonino@gmail.com'
git config --global init.defaultBranch main
```