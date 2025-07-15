## Criando o ambiente virtual

```
cd  ~/app_repo
git pull origin <branch>
python3.9 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
pip install psycopg2
pip install gunicorn
```

## Configurando o nginx

Use o arquivo e as explicações disponibilizadas na aula.