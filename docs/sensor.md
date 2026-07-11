# Sensor API Spec

## Get Latest Sensor Data

Endpoint : GET /api/zones/{zone_id}/sensor/latest

Request Header :
- Authorization : Bearer {token}

Response Body (Success - 200) :

```json
{
  "id" : 150,
  "zone_id" : 1,
  "kelembapan_tanah" : 65.2,
  "suhu_udara" : 31.5,
  "kelembapan_udara" : 78.0,
  "ph_tanah" : 6.8,
  "intensitas_cahaya" : 1200,
  "status_hujan" : false,
  "debit_air" : 0.0,
  "waktu_rekam" : "2026-07-11 10:30:00+00:00"
}
```

Response Body (Failed - 404) :

```json
{
  "detail" : "Belum ada data sensor untuk Zona 1"
}
```

Response Body (Failed - 401) :

```json
{
  "detail" : "Sesi Anda telah habis atau token tidak valid. Silakan login kembali."
}
```

## Get Sensor History

Endpoint : GET /api/zones/{zone_id}/sensor/history?limit=20

Query Parameters :
- `limit` : integer (default: 20) — jumlah data terakhir yang diambil

Request Header :
- Authorization : Bearer {token}

Response Body (Success - 200) :

```json
[
  {
    "id" : 150,
    "zone_id" : 1,
    "kelembapan_tanah" : 65.2,
    "suhu_udara" : 31.5,
    "kelembapan_udara" : 78.0,
    "ph_tanah" : 6.8,
    "intensitas_cahaya" : 1200,
    "status_hujan" : false,
    "debit_air" : 0.0,
    "waktu_rekam" : "2026-07-11 10:30:00+00:00"
  },
  {
    "id" : 149,
    "zone_id" : 1,
    "kelembapan_tanah" : 64.8,
    "suhu_udara" : 31.2,
    "kelembapan_udara" : 78.5,
    "ph_tanah" : 6.8,
    "intensitas_cahaya" : 1150,
    "status_hujan" : false,
    "debit_air" : 0.0,
    "waktu_rekam" : "2026-07-11 10:25:00+00:00"
  }
]
```

Sorted secara kronologis ascending (data terlama lebih dulu).
