# Pump API Spec

## Get Pump Logs

Endpoint : GET /api/zones/{zone_id}/pump/logs?limit=10

Query Parameters :
- `limit` : integer (default: 10) — jumlah log terakhir

Request Header :
- Authorization : Bearer {token}

Response Body (Success - 200) :

```json
[
  {
    "id" : 25,
    "zone_id" : 1,
    "status_pompa" : "ON",
    "dipicu_oleh" : "Otomatis (Threshold Bawah)",
    "waktu_kejadian" : "2026-07-11 10:30:05+00:00"
  },
  {
    "id" : 24,
    "zone_id" : 1,
    "status_pompa" : "OFF",
    "dipicu_oleh" : "Otomatis (Threshold Atas)",
    "waktu_kejadian" : "2026-07-11 09:15:30+00:00"
  }
]
```

Response Body (Failed - 401) :

```json
{
  "detail" : "Sesi Anda telah habis atau token tidak valid. Silakan login kembali."
}
```

## Control Pump

Endpoint : POST /api/pump/control

Request Header :
- Authorization : Bearer {token} (Admin / Super Admin)

Request Body :

```json
{
  "zone_id" : 1,
  "status_pompa" : "ON",
  "dipicu_oleh" : "Admin Manual"
}
```

Response Body (Success - 200) :

```json
{
  "message" : "Instruksi ON berhasil dikirim",
  "topik" : "borneo/zona-1/pompa"
}
```

Response Body (Failed - 500) :

```json
{
  "detail" : "Gagal mengirim instruksi ke perangkat."
}
```

Response Body (Failed - 403) :

```json
{
  "detail" : "Akses Ditolak! Fitur ini khusus untuk Eksekutor (Admin / Super Admin)."
}
```

### Notes

- `status_pompa` : `"ON"` atau `"OFF"`
- `dipicu_oleh` : teks bebas untuk mencatat pemicu (contoh: `"Admin Manual"`, `"Otomatis (Threshold Bawah)"`, `"Penjadwalan"`)
- Perintah dikirim via MQTT ke topic `borneo/zona-{zone_id}/pompa`
