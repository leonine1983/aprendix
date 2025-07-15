###############################################################################
# Replace
# upa_gunicorn to the name of the gunicorn file you want
# matiasaildo to your user name
# app_repo to the folder name of your project
# upa to the folder name where you find a file called wsgi.py
#
###############################################################################
# Criando o arquivo upa_gunicorn.socket
sudo nano /etc/systemd/system/upa_gunicorn.socket

###############################################################################
# Conteúdo do arquivo
[Unit]
Description=gunicorn blog socket

[Socket]
ListenStream=/run/upa_gunicorn.socket

[Install]
WantedBy=sockets.target

###############################################################################
# Criando o arquivo upa_gunicorn.service
sudo nano /etc/systemd/system/upa_gunicorn.service

###############################################################################
# Conteúdo do arquivo
[Unit]
Description=Gunicorn daemon (You can change if you want)
Requires=upa_gunicorn.socket
After=network.target

[Service]
User=matiasaildo
Group=www-data
Restart=on-failure
EnvironmentFile=/home/matiasaildo/app_repo/.env
WorkingDirectory=/home/matiasaildo/app_repo
# --error-logfile --enable-stdio-inheritance --log-level and --capture-output
# are all for debugging purposes.
ExecStart=/home/matiasaildo/app_repo/venv/bin/gunicorn \
          --error-logfile /home/matiasaildo/app_repo/gunicorn-error-log \
          --enable-stdio-inheritance \
          --log-level "debug" \
          --capture-output \
          --access-logfile - \
          --workers 6 \
          --bind unix:/run/upa_gunicorn.socket \
          upa.wsgi:application

[Install]
WantedBy=multi-user.target

###############################################################################
# Ativando
sudo systemctl start upa_gunicorn.socket
sudo systemctl enable upa_gunicorn.socket

# Checando
sudo systemctl status upa_gunicorn.socket
curl --unix-socket /run/upa_gunicorn.socket localhost
sudo systemctl status upa_gunicorn

# Restarting
sudo systemctl restart upa_gunicorn.service
sudo systemctl restart upa_gunicorn.socket
sudo systemctl restart upa_gunicorn

# After changing something (Depois que mudar alguma coisa de fazer esse codigo abaixo)
sudo systemctl daemon-reload

# Debugging
sudo journalctl -u upa_gunicorn.service
sudo journalctl -u upa_gunicorn.socket