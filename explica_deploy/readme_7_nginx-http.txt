# https://www.nginx.com/blog/using-free-ssltls-certificates-from-lets-encrypt-with-nginx/
#
#PARA CONFIGURAR O NGINX
#sudo nano /etc/nginx/sites-available/upa
#sudo ln -s /etc/nginx/sites-available/upa /etc/nginx/sites-enabled/upa 
#sudo nginx -t
# sudo systemctl restart nginx
#cd /etc/nginx/sites-available/upa 
# REPLACES
# 34.95.242.9 = Replace with your domain
# /home/matiasaildo/app_repo = Replace with the path to the folder for the project
# /home/matiasaildo/app_repo/static = Replace with the path to the folder for static files
# /home/matiasaildo/app_repo/media = Replace with the path to the folder for media files
# upa_gunicorn.socket = Replace with your unix socket name
# 
# Set timezone
# List - timedatectl list-timezones
# sudo timedatectl set-timezone America/Sao_Paulo
#
# HTTP
server {
  listen 80;
  listen [::]:80;
  server_name 34.95.242.9;

  # Add index.php to the list if you are using PHP
  index index.html index.htm index.nginx-debian.html index.php;
  
  # ATTENTION: /home/matiasaildo/app_repo/static
  location /static {
    autoindex on;
    alias /home/matiasaildo/app_repo/static;
  }

  # ATTENTION: /home/matiasaildo/app_repo/media 
  location /media {
    autoindex on;
    alias /home/matiasaildo/app_repo/media;
  }

  # ATTENTION: upa_gunicorn.socket
  location / {
    proxy_pass http://unix:/run/upa_gunicorn.socket;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
  }

  # deny access to .htaccess files, if Apache's document root
  # concurs with nginx's one
  #
  location ~ /\.ht {
    deny all;
  }

  location ~ /\. {
    access_log off;
    log_not_found off;
    deny all;
  }

  gzip on;
  gzip_disable "msie6";

  gzip_comp_level 6;
  gzip_min_length 1100;
  gzip_buffers 4 32k;
  gzip_proxied any;
  gzip_types
    text/plain
    text/css
    text/js
    text/xml
    text/javascript
    application/javascript
    application/x-javascript
    application/json
    application/xml
    application/rss+xml
    image/svg+xml;

  #access_log  /var/log/nginx/34.95.242.9-access.log;
  error_log   /var/log/nginx/34.95.242.9-error.log;
}