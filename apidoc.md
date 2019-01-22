### API DOC

1. To use Rest API you need to create oauth2 credentials.
```
-   Under http://127.0.0.1:8000/admin/oauth2_provider/application/ click 'ADD APPLICATION'

-   Do not change 'client_id' & 'client_secret' (They will be used for generate access token to use in your requests header)

-   Select the following settings to create application:
    Client Type -> Confidential
    Authorization grant type ->  Resource owner password-based
    Name -> Whatever you want   
```

2. AUTHENTICATION
```
You need to generate an access token and add it as a Bearer header in your requests. See the Postman Collection for how to
generate an access token.

***
For testing purposes Google's playground system can be used for gathering dummy access tokens to use on this API. 
***

```

3. Postman Collection
```
https://www.getpostman.com/collections/2bb6572a9df9802168a8
```