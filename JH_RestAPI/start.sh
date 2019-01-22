# Start Postgres
pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start

python3 manage.py runserver &
python3 manage.py process_tasks