import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# 1. Membaca isi file .env
load_dotenv()

# 2. Mengambil alamat database (DB_URL) dari .env (default ke host.docker.internal jika tidak ditemukan)
SQLALCHEMY_DATABASE_URL = os.getenv("DB_URL", "mysql+pymysql://root:@host.docker.internal:3306/db_borneo")

# 3. Membuat "Mesin Utama" untuk terhubung ke MySQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 4. Membuat pabrik sesi (untuk membuka dan menutup koneksi secara aman)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Membuat kertas cetak biru kosong (Nanti dipakai oleh models.py)
Base = declarative_base()

# 6. Fungsi khusus agar setiap kali aplikasi meminta data, pintu database dibuka dan ditutup otomatis
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()