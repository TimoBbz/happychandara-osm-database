sudo apt-get install python3 python3-pip python3-venv nginx postgresql libpq-dev
sudo pg_ctlcluster 12 main start
sudo cp pg_hba.conf /etc/postgresql/12/main/
sudo systemctl restart postgresql
psql -h localhost -U postgres -c "CREATE ROLE django PASSWORD 'django'"
createdb -h localhost -U postgres -O django osm
python3 -m venv /var/www/osm_database/env
sudo pip3 install uwsgi
sudo uwsgi --ini uwsgi.ini
sudo cp osm_database.nginx /etc/nginx/sites-available
sudo rm /etc/nginx/sites-enabled/osm_database.nginx
sudo ln -s /etc/nginx/sites-available/osm_database.nginx /etc/nginx/sites-enabled/osm_database.nginx
sudo systemctl restart nginx
