### Quickstart

1. Install Postgres database depending on your [OS](https://www.postgresql.org/download/):
```
brew install postgres
```

2. Run install script located in /JH_RestAPI directory:
```
./install.sh
```

3. Make sure your Postgres is running:
```
# Start Postgres
pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start
```

4. Start server located in /JH_RestAPI directory:
```
./start.sh
```

5. [To see API DOC](/apidoc.md)
