# https://www.nginx.com/blog/using-free-ssltls-certificates-from-lets-encrypt-with-nginx/
#
# REPLACES
# www.cauans-technology.com = Replace with your domain
# /home/matiasaildo/app_repo = Replace with the path to the folder for the project
# /home/matiasaildo/app_repo/static = Replace with the path to the folder for static files
# /home/matiasaildo/app_repo/media = Replace with the path to the folder for media files
# upa_gunicorn.socket = Replace with your unix socket name
# 
# For letsencrypt and Ubuntu:
# sudo apt update -y && sudo apt upgrade -y && sudo apt autoremove -y
# sudo apt install nginx certbot python3-certbot-nginx -y
# sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 4096
# sudo systemctl stop nginx
# sudo certbot certonly --standalone -d www.cauans-technology.com
# sudo chmod -R 755 /home/matiasaildo/app_repo
# sudo nano /etc/nginx/sites-available/www.cauans-technology.com
# Add contents of this file
# sudo ln -s /etc/nginx/sites-available/www.cauans-technology.com /etc/nginx/sites-enabled/www.cauans-technology.com
#

#IMPORTANT NOTES:
 
# - Congratulations! Your certificate and chain have been saved at:
#   /etc/letsencrypt/live/www.cauans-technology.com/fullchain.pem
#   Your key file has been saved at:
#   /etc/letsencrypt/live/www.cauans-technology.com/privkey.pem
#   Your cert will expire on 2023-07-24. To obtain a new or tweaked
#   version of this certificate in the future, simply run certbot
#   again. To non-interactively renew *all* of your certificates, run
#   "certbot renew"
# - Your account credentials have been saved in your Certbot
#   configuration directory at /etc/letsencrypt. You should make a
#   secure backup of this folder now. This configuration directory will
#   also contain certificates and private keys obtained by Certbot so
#   making regular backups of this folder is ideal.
# - If you like Certbot, please consider supporting our work by:

#   Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
#   Donating to EFF:                    https://eff.org/donate-le




# Set timezone
# List - timedatectl list-timezones
# sudo timedatectl set-timezone America/Sao_Paulo
#
# HTTP
server {
  listen 80;
  listen [::]:80;
  server_name www.cauans-technology.com;
  return 301 https://$host$request_uri;
}

# HTTPS
server {
  listen 443 ssl http2;
  listen [::]:443 ssl http2;

  server_name www.cauans-technology.com;

  ssl_certificate /etc/letsencrypt/live/www.cauans-technology.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/www.cauans-technology.com/privkey.pem;
  ssl_trusted_certificate /etc/letsencrypt/live/www.cauans-technology.com/chain.pem;

  # Improve HTTPS performance with session resumption
  ssl_session_cache shared:SSL:10m;
  ssl_session_timeout 5m;

  # Enable server-side protection against BEAST attacks
  ssl_prefer_server_ciphers on;
  ssl_ciphers ECDH+AESGCM:ECDH+AES256:ECDH+AES128:DH+3DES:!ADH:!AECDH:!MD5;

  # Disable SSLv3
  ssl_protocols TLSv1 TLSv1.1 TLSv1.2;

  # Diffie-Hellman parameter for DHE ciphersuites
  # $ sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 4096
  ssl_dhparam /etc/ssl/certs/dhparam.pem;

  # Enable HSTS (https://developer.mozilla.org/en-US/docs/Security/HTTP_Strict_Transport_Security)
  add_header Strict-Transport-Security "max-age=63072000; includeSubdomains";

  # Enable OCSP stapling (http://blog.mozilla.org/security/2013/07/29/ocsp-stapling-in-firefox)
  ssl_stapling on;
  ssl_stapling_verify on;
  resolver 8.8.8.8 8.8.4.4 valid=300s;
  resolver_timeout 5s;

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

  access_log off;
  #access_log  /var/log/nginx/www.cauans-technology.com-access.log;
  error_log   /var/log/nginx/www.cauans-technology.com-error.log;
}