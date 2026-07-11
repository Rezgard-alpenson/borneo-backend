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

| File | Fungsi |
|---|---|
| `main.py` | Entry point FastAPI |
| `database.py` | Koneksi MySQL via SQLAlchemy |
| `models.py` | Definisi tabel database |
| `mqtt.py` | Koneksi & handler MQTT |
| `alembic/` | Konfigurasi migration |
