### Quickstart

1. Install Postgres database depending on your [OS](https://www.postgresql.org/download/):
```
brew install postgres
```

2. Make sure your Postgres is running:
```
# Start Postgres
initdb /usr/local/var/postgres
pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start
```

3. Add the variables below to your environment variables (all optional but you need to add them to use these features):
```
export JOBHAX_CLEARBIT_KEY=/*key*/ # to get/verify company logo&name from ClearBit API.
export EMAIL_HOST_USER=/*test@gmail.com*/ # to send activation or reset password email to the user (should be Google Mail)
export EMAIL_HOST_PASSWORD=/*password*/  # to send activation or reset password email to the user
export JOBHAX_RECAPTCHA_SECRET=/*recaptcha_secret*/ # to verify recaptcha token coming from the user request

[How to add variables to your Environment Variables](https://medium.com/@himanshuagarwal1395/setting-up-environment-variables-in-macos-sierra-f5978369b255)
```

4. Run install script located in /JH_RestAPI directory:
```
./install.sh
```

5. Start server located in /JH_RestAPI directory:
```
./start.sh
```

6. [To see API DOC](/apidoc.md)
