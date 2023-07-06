echo "updating nginx"

sudo cp scripts/nginx.conf /etc/nginx

sudo nginx -t
sudo service nginx restart
