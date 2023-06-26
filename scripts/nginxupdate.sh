echo "updating nginx"

sudo cp nginx.conf /etc/nginx

sudo nginx -t
sudo service nginx restart
