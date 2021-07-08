# OSM database

## Deployment

1. Install the required packages on the server:
`sudo apt-get install python3 python3-pip python3-venv nginx postgresql libpq-dev`

3. Put the sources on the right folder: (execute this command from the sources directory on your computer)
`rsync -rC . 192.168.4.231:/var/www/osm_database`

2. Start and configure PostgreSQL:
```bash
sudo pg_ctlcluster 12 main start
sudo cp /var/www/osm_database/pg_hba.conf /etc/postgresql/12/main/
sudo systemctl restart postgresql
psql -h localhost -U postgres -c "CREATE ROLE django PASSWORD 'django'"
createdb -h localhost -U postgres -O django osm
```

3. Install python environment:
```bash
python3 -m venv /var/www/osm_database/env
source /var/www/osm_database/env
pip install -r /var/www/osm_database/requirements.txt
python manage.py collectstatic
python manage.py migrate
deactivate
```

4. Configure and launch Gunicorn:
```bash
sudo cp /var/www/osm_database/gunicorn.service /etc/systemd/system
sudo systemctl restart gunicorn 
```

5. Configure and launch Nginx:
```bash
sudo cp /var/www/osm_database/nginx.conf /etc/nginx/
sudo systemctl restart nginx
```

6. Add the API host in the hosts file
```bash
sudo echo 192.168.4.181 api-sim.happychandara.org >> /etc/hosts
```

## Managing

### How does the server works

The structure follow this scheme:

```ascii
  PostgreSQL    Website
      /|\          |
       |           |
       |       Gunicorn                         
       |      /        \          
      \|/    /          \                  
127.0.0.1:5432         127.0.0.1:8000 <--Nginx--> 192.168.4.231 <--Clients
```
The website is run by Gunicorn, that serves it in localhost (127.0.0.1:8000), and communicates with the database (127.0.0.1:5432). Then, Nginx proxies it to 192.168.4.231 in order to serve it to the clients.

### Debugging

If the server is unreachable, you have to find out where it is broken. First, connect on the server, then check if the website is served in local with the command `curl http://127.0.0.1:8000`.

If it is working, the issue comes from Nginx. Restart its service with `sudo systemctl restart nginx`. If it's not working, check the journal `sudo journalctl -xeu nginx`, and the error will appear.

Else, it comes either from Gunicorn or the website. Do the same as above replacing _nginx_ with _gunicorn_, then with _postgresql_.

If the error is not simply a stopped service, then a whole range of error can occure. You can search the errors on google to get informations on how to solve them.
