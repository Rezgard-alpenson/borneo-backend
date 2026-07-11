# Auth API Spec

## Login

Endpoint : POST /api/login

Request Body :

```json
{
  "username" : "petani1",
  "password" : "rahasia"
}
```

Response Body (Success - 200) :

```json
{
  "message" : "Login berhasil!",
  "access_token" : "eyJhbGciOiJIUzI1NiIs...",
  "token_type" : "bearer",
  "user_id" : 1,
  "role" : "petani",
  "username" : "petani1"
}
```

Response Body (Failed - 401) :

```json
{
  "detail" : "Username atau password salah"
}
```
