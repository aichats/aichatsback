sudo apt update
sudo apt install software-properties-common -y
sudo add-apt-repository universe
sudo add-apt-repository ppa:certbot/certbot
sudo apt update -y
sudo apt install python3-certbot-nginx

sudo cp ~/aichat/scripts/nginx.conf /etc/nginx

sudo apt install certbot -y

#Certbot will guide you through the certificate issuance process, including domain verification and configuration setup.
sudo certbot --nginx

#Automatic renewal (optional): Certbot can automatically renew your certificates before they expire. It is recommended to set up an automatic renewal process. To do this, Certbot provides a certbot command that you can run periodically from a cron job. For example:
sudo certbot renew --quiet
