# Locally:

python .\main.py

ngrok http 8000

# Server

cd /srv/battlesnakebot
git pull
chown -R www-data:www-data /srv/battlesnakebot

systemctl reload battlesnakebot

more invasive:
systemctl restart battlesnakebot