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
```
[How to add variables to your Environment Variables](https://medium.com/@himanshuagarwal1395/setting-up-environment-variables-in-macos-sierra-f5978369b255)

4. Run install script located in /JH_RestAPI directory:
```
./install.sh
```

5. Start server located in /JH_RestAPI directory:
```
./start.sh
```

6. To use Rest API you need to create oauth2 credentials.
```
-   Under http://localhost:8000/admin/oauth2_provider/application/ click 'ADD APPLICATION'

-   Do not change 'client_id' & 'client_secret' (They will be used for generate access token to use in your requests header)

-   Select the following settings to create application:
    Client Type -> Confidential
    Authorization grant type ->  Resource owner password-based
    Name -> Whatever you want   
```

7. AUTHENTICATION
```
You need to generate an access token and add it as a Bearer header in your requests. See the Postman Collection for how to
generate an access token.

For testing purposes Google's playground system can be used for gathering dummy access tokens to use on this API.

You will need to grant following permissions:
- https://www.googleapis.com/auth/userinfo.email
- https://www.googleapis.com/auth/userinfo.profile
- https://www.googleapis.com/auth/gmail.readonly
```

[OAuth 2.0 Playground](https://developers.google.com/oauthplayground/) 

8. [Postman Collection](https://www.getpostman.com/collections/2bb6572a9df9802168a8)

9. [API Documentation](https://github.com/job-hax/docs/blob/master/3.backend_api.md)
