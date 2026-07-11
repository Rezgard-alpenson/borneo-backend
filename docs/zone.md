# Zone API Spec

## Get All Zones

Endpoint : GET /api/zones

Request Header :
- Authorization : Bearer {token}

Response Body (Success - 200) :

```json
[
  {
    "id" : 1,
    "nama_zona" : "Lahan A",
    "deskripsi" : "Lahan tomat bagian utara",
    "mac_address" : "AA:BB:CC:DD:EE:FF",
    "batas_bawah" : 40.0,
    "batas_atas" : 80.0
  },
  {
    "id" : 2,
    "nama_zona" : "Lahan B",
    "deskripsi" : "Lahan cabai bagian selatan",
    "mac_address" : "11:22:33:44:55:66",
    "batas_bawah" : 35.0,
    "batas_atas" : 75.0
  }
]
```

Response Body (Failed - 401) :

```json
{
  "detail" : "Sesi Anda telah habis atau token tidak valid. Silakan login kembali."
}
```

## Create Zone

Endpoint : POST /api/zones/create

Request Header :
- Authorization : Bearer {token} (Admin / Super Admin)

Request Body :

```json
{
  "nama_zona" : "Lahan C",
  "deskripsi" : "Lahan terong",
  "mac_address" : "AA:BB:CC:DD:EE:11",
  "batas_bawah" : 40.0,
  "batas_atas" : 80.0
}
```

Response Body (Success - 200) :

```json
{
  "message" : "Zona baru berhasil ditambahkan!",
  "zone_id" : 3,
  "mac_address" : "AA:BB:CC:DD:EE:11"
}
```

Response Body (Failed - 400) :

```json
{
  "detail" : "Perangkat dengan MAC Address 'AA:BB:CC:DD:EE:11' sudah terdaftar!"
}
```

## Get Zone by ID

Endpoint : GET /api/zones/{zone_id}

Request Header :
- Authorization : Bearer {token}

Response Body (Success - 200) :

```json
{
  "id" : 1,
  "nama_zona" : "Lahan A",
  "deskripsi" : "Lahan tomat bagian utara",
  "mac_address" : "AA:BB:CC:DD:EE:FF",
  "batas_bawah" : 40.0,
  "batas_atas" : 80.0
}
```

Response Body (Failed - 404) :

```json
{
  "detail" : "Zona tidak ditemukan!"
}
```

## Update Zone

Endpoint : PUT /api/zones/{zone_id}

Request Header :
- Authorization : Bearer {token} (Admin / Super Admin)

Request Body :

```json
{
  "nama_zona" : "Lahan A Updated",
  "deskripsi" : "Deskripsi baru",
  "mac_address" : "AA:BB:CC:DD:EE:FF",
  "batas_bawah" : 30.0,
  "batas_atas" : 70.0
}
```

Semua field bersifat opsional.

Response Body (Success - 200) :

```json
{
  "message" : "Pengaturan threshold zona berhasil diperbarui!",
  "zone" : {
    "id" : 1,
    "nama_zona" : "Lahan A Updated",
    "deskripsi" : "Deskripsi baru",
    "mac_address" : "AA:BB:CC:DD:EE:FF",
    "batas_bawah" : 30.0,
    "batas_atas" : 70.0
  }
}
```

Response Body (Failed - 404) :

```json
{
  "detail" : "Zona tidak ditemukan!"
}
```

## Get Zone Alerts

Endpoint : GET /api/zones/{zone_id}/alerts

Request Header :
- Authorization : Bearer {token}

Response Body (Success - 200) :

```json
{
  "zone_id" : 1,
  "nama_zona" : "Lahan A",
  "alerts" : [
    {
      "severity" : "CRITICAL",
      "title" : "DARURAT: Tanah Terlalu Kering!",
      "message" : "Kelembapan tanah saat ini 25.0% berada di bawah batas minimal (40.0%). Pompa otomatis diinstruksikan ON.",
      "timestamp" : "2026-07-11 10:30:00+00:00"
    },
    {
      "severity" : "WARNING",
      "title" : "Peringatan Suhu Udara Panas!",
      "message" : "Suhu udara terdeteksi 35.2°C. Waspadai laju penguapan air berlebih pada zona ini.",
      "timestamp" : "2026-07-11 10:30:00+00:00"
    },
    {
      "severity" : "INFO",
      "title" : "Aktivitas Pompa: ON",
      "message" : "Instruksi pompa terakhir dipicu oleh: Otomatis (Threshold Bawah).",
      "timestamp" : "2026-07-11 10:30:05+00:00"
    }
  ]
}
```

Response Body (Failed - 404) :

```json
{
  "detail" : "Zona tidak ditemukan!"
}
```

### Alert Severity Levels

| Severity | Keterangan |
|----------|------------|
| `CRITICAL` | Darurat — kelembapan tanah di bawah batas bawah |
| `WARNING` | Peringatan — suhu udara > 33°C |
| `INFO` | Informasi — kelembapan di atas batas atas, hujan terdeteksi, atau aktivitas pompa |
| `SAFE` | Aman — kondisi lahan dalam rentang optimal |

## Export Sensor Data CSV

Endpoint : GET /api/zones/{zone_id}/export/sensor

Request Header :
- Authorization : Bearer {token}

Response : File download `laporan_sensor_zona_{zone_id}.csv` (Content-Type: text/csv)

Response Body (Failed - 404) :

```json
{
  "detail" : "Zona tidak ditemukan!"
}
```
