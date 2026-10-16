#!/usr/bin/env bash
# Sets up the web servers for the deployment of web_static (Nginx, /data tree)

if ! command -v nginx > /dev/null 2>&1; then
    apt-get update -y
    apt-get install -y nginx
fi

mkdir -p /data/web_static/releases/test/ /data/web_static/shared/

cat > /data/web_static/releases/test/index.html << 'HTML'
<html>
  <head>
  </head>
  <body>
    Holberton School
  </body>
</html>
HTML

# the symbolic link is deleted and recreated on every run
rm -rf /data/web_static/current
ln -s /data/web_static/releases/test/ /data/web_static/current

chown -R ubuntu:ubuntu /data/

# serve /data/web_static/current/ at /hbnb_static (only added once)
config="/etc/nginx/sites-available/default"
if ! grep -q "location /hbnb_static" "$config"; then
    sed -i '0,/server_name .*;/s//&\n\n\tlocation \/hbnb_static {\n\t\talias \/data\/web_static\/current\/;\n\t}/' "$config"
fi

service nginx restart > /dev/null 2>&1 || nginx -s reload > /dev/null 2>&1

exit 0
