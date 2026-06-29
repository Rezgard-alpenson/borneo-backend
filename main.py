import mqtt # Memanggil file mqtt.py yang baru kita buat
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException 
from pydantic import BaseModel 
from sqlalchemy.orm import Session 
from passlib.context import CryptContext
from database import engine, SessionLocal
import models

models.Base.metadata.create_all(bind=engine)

# 1. Konfigurasi Alat Pengacak Sandi (Bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

# 2. Dependency Database (Pembuka & Penutup Koneksi untuk setiap Request API)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 3. LOGIKA PENYEMAIAN DATA & INISIALISASI IOT
@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    
    # --- MENYALAKAN KONEKSI MQTT SAAT SERVER START ---
    mqtt.connect_mqtt() 
    # -------------------------------------------------
    
    try:
        # Cek apakah tabel users masih kosong dengan mencari akun "superadmin"
        admin_exist = db.query(models.User).filter(models.User.username == "superadmin").first()
        
        if not admin_exist:
            # Jika kosong, ciptakan "Nenek Moyang" Super Admin
            hashed_password = get_password_hash("admin123")
            super_admin = models.User(
                username="superadmin",
                password_hash=hashed_password,
                role="super_admin",
                is_active=True
            )
            db.add(super_admin)
            db.commit()
            print(">>> STATUS: Akun Super Admin pertama BERHASIL diciptakan! <<<")
        else:
            print(">>> STATUS: Penyemaian dilewati, Super Admin sudah ada. <<<")
    finally:
        db.close()
    
    yield # Mengizinkan server berjalan

# 4. INISIALISASI APLIKASI FASTAPI
app = FastAPI(
    title="Borneo Agricola API",
    description="Backend Server untuk Sistem Cerdas IoT Pertanian",
    version="1.0.0",
    lifespan=lifespan
)

# 5. Schema Pydantic (Format Data JSON)
class UserCreate(BaseModel):
    username: str
    password: str
    role: str # "admin" atau "user"
    pembuat_id: int

# Schema Baru: Format JSON untuk kontrol pompa MQTT
class PumpControl(BaseModel):
    zone_id: int
    status_pompa: str # Harus berisi "ON" atau "OFF"
    dipicu_oleh: str # Contoh: "Manual (Aplikasi)" atau "Otomatis (Sensor)"

# 6. RUTE PENGUJIAN AWAL
@app.get("/")
def ping_server():
    return {
        "status": "sukses",
        "pesan": "Mesin Utama Borneo Agricola Berjalan Sempurna!"
    }

# 7. RUTE PEMBUATAN AKUN BARU SEKALIGUS CATAT CCTV
@app.post("/api/users/create")
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    
    # Validasi: Apakah username sudah dipakai?
    cek_user = db.query(models.User).filter(models.User.username == user.username).first()
    if cek_user:
        raise HTTPException(status_code=400, detail="Username sudah terdaftar!")

    # Proses Insert ke Tabel User
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        password_hash=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Proses Insert ke Tabel CCTV
    log_aksi = f"Mendaftarkan akun baru dengan username: {user.username} sebagai {user.role}"
    db_log = models.UserLog(
        user_id=user.pembuat_id, 
        action=log_aksi
    )
    db.add(db_log)
    db.commit()

    return {"message": "Akun berhasil dibuat dan tindakan telah dicatat di sistem!", "user_id": db_user.id}

# 8. RUTE KONTROL POMPA & PENCATATAN LOG KE DATABASE
@app.post("/api/pump/control")
def control_pump(req: PumpControl, db: Session = Depends(get_db)):
    
    # 1. Kirim Perintah ke ESP32 via MQTT terlebih dahulu
    topik_tujuan = f"borneo/zona-{req.zone_id}/pompa"
    pesan_instruksi = req.status_pompa
    
    sukses_terkirim = mqtt.publish_command(topic=topik_tujuan, payload=pesan_instruksi)
    
    if not sukses_terkirim:
        raise HTTPException(status_code=500, detail="Gagal mengirim instruksi ke perangkat alat di lahan.")

    # 2. Jika sukses terkirim, catat di Database (CCTV Riwayat Pompa)
    db_log = models.PumpLog(
        zone_id=req.zone_id,
        status_pompa=req.status_pompa,
        dipicu_oleh=req.dipicu_oleh
    )
    db.add(db_log)
    db.commit()

    return {
        "message": f"Instruksi {req.status_pompa} berhasil dikirim ke perangkat",
        "topik": topik_tujuan
    }

# =====================================================================
# 9. RUTE API UNTUK FLUTTER (DASHBOARD MOBILE)
# =====================================================================

@app.get("/api/zones/{zone_id}/sensor/latest")
def get_latest_sensor_data(zone_id: int, db: Session = Depends(get_db)):
    """Mengambil 1 data sensor paling terakhir masuk berdasarkan zone_id"""
    data = db.query(models.SensorData)\
             .filter(models.SensorData.zone_id == zone_id)\
             .order_by(models.SensorData.waktu_rekam.desc())\
             .first()
             
    if not data:
        raise HTTPException(status_code=404, detail=f"Belum ada data sensor untuk Zona {zone_id}")
    return data

@app.get("/api/zones/{zone_id}/pump/logs")
def get_pump_logs_history(zone_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """Mengambil riwayat aktivitas pompa air di zona tertentu"""
    return db.query(models.PumpLog)\
             .filter(models.PumpLog.zone_id == zone_id)\
             .order_by(models.PumpLog.waktu_kejadian.desc())\
             .limit(limit)\
             .all()

@app.get("/api/zones")
def get_all_registered_zones(db: Session = Depends(get_db)):
    """Memuat seluruh daftar zona untuk dropdown aplikasi"""
    return db.query(models.Zone).all()