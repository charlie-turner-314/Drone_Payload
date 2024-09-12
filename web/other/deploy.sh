#!/bin/bash

# Enforce run as root
if [ "$EUID" -ne 0 ]
  then echo "Deploy script must be run as root"
  exit
fi

# Deploy UWSGI Server
rm -rf deploy/
cp -r src/ deploy/
chown -R www-data:www-data deploy/

# Deploy NGINX config
rm /etc/nginx/sites-available/egh455-web
cp egh455-web.nginx /etc/nginx/sites-available/egh455-web
ln -sf /etc/nginx/sites-available/egh455-web /etc/nginx/sites-enabled/egh455-web
