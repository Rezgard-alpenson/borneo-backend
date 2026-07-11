# Borneo Backend

## Persyaratan

- Python 3.10+
- MySQL (buat database `db_borneo`)
- Mosquitto MQTT broker (opsional, untuk IoT)

## Cara Menjalankan

### Opsi 1: Manual (tanpa Docker)

```bash
# Copy env
cp .env.example .env

# Aktifkan virtual env
source venv/bin/activate

# Apply migration
alembic upgrade head

# Jalankan server
uvicorn main:app --host localhost --port 8000 --reload
```

### Opsi 2: Docker Compose

```bash
docker compose up --build
```

> Dengan Docker, migration otomatis jalan? **Belum.** Masuk ke container dulu:
> ```bash
> docker exec -it borneo_backend alembic upgrade head
> ```

Server akan berjalan di `http://localhost:8000`.

## Database

Tabel **tidak** otomatis terbuat. Harus di-create manual via Alembic:

```bash
# Buat migration baru (setelah ubah models.py)
alembic revision --autogenerate -m "pesan_perubahan"

# Apply migration
alembic upgrade head
```

## Struktur

```text
.
├── main.py            # Entry point FastAPI
├── alembic.ini        # Konfigurasi Alembic migration
├── docker-compose.yml # Setup service via Docker Compose
├── Dockerfile         # Docker image definition
├── requirements.txt   # Daftar dependency Python
├── app/               # Source code utama aplikasi
│   ├── main.py        # Inisialisasi app dan routing utama
│   ├── auth.py        # Logika autentikasi
│   ├── middleware.py  # Middleware request/response
│   ├── mqtt.py        # Koneksi dan handler MQTT
│   ├── schemas.py     # Pydantic schema
│   ├── seed.py        # Data awal / seeding
│   ├── config/        # Konfigurasi aplikasi
│   ├── models/        # Model database SQLAlchemy
│   ├── routes/        # Endpoint API
│   └── services/      # Business logic
├── alembic/           # Folder migration Alembic
│   └── versions/      # File-file migration
└── mosquitto/         # Konfigurasi broker MQTT
```
