# User API Spec

## Create User

Endpoint : POST /api/users/create

Request Header :
- Authorization : Bearer {token} (Admin / Super Admin)

Request Body :

```json
{
  "username" : "petani1",
  "email" : "petani1@example.com",
  "password" : "rahasia",
  "role" : "petani",
  "pembuat_id" : 1
}
```

Response Body (Success - 200) :

```json
{
  "message" : "Akun berhasil dibuat",
  "user_id" : 2
}
```

Response Body (Failed - 400) :

```json
{
  "detail" : "Username sudah terdaftar!"
}
```

Response Body (Failed - 403) :

```json
{
  "detail" : "Akses Ditolak! Fitur ini khusus untuk Eksekutor (Admin / Super Admin)."
}
```

## Change Password

Endpoint : POST /api/users/change-password

Request Header :
- Authorization : Bearer {token}

Request Body :

```json
{
  "old_password" : "rahasiaLama",
  "new_password" : "rahasiaBaru"
}
```

Response Body (Success - 200) :

```json
{
  "message" : "Password berhasil diperbarui secara rahasia!"
}
```

Response Body (Failed - 400) :

```json
{
  "detail" : "Password lama salah! Mohon periksa kembali password lama Anda."
}
```

Response Body (Failed - 401) :

```json
{
  "detail" : "Sesi Anda telah habis atau token tidak valid. Silakan login kembali."
}
```
