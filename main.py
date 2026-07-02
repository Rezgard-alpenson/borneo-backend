import mqtt 
import io
import csv
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel 
from typing import Optional
from sqlalchemy.orm import Session 
from sqlalchemy import text
from passlib.context import CryptContext
from database import engine, SessionLocal
import models
import auth

models.Base.metadata.create_all(bind=engine)

# 1. Konfigurasi Alat Pengacak Sandi (Bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

# 2. Dependency Database
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
    mqtt.connect_mqtt() 
    try:
        try:
            db.execute(text("ALTER TABLE zones ADD COLUMN mac_address VARCHAR(50);"))
            db.commit()
            print(">>> STATUS DB: Kolom 'mac_address' berhasil ditambahkan ke tabel zones! <<<")
        except Exception:
            db.rollback()

        try:
            db.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(100);"))
            db.commit()
            print(">>> STATUS DB: Kolom 'email' berhasil ditambahkan ke tabel users! <<<")
        except Exception:
            db.rollback()

        # Cek apakah zona pertama sudah punya MAC address
        zona1 = db.query(models.Zone).filter(models.Zone.id == 1).first()
        if zona1 and not zona1.mac_address:
            zona1.mac_address = "ESP32-ZONA-01"
            db.commit()

        all_users = db.query(models.User).all()
        print(f"\n>>> [INFO DB XAMPP] Daftar User di Database saat ini: {[u.username for u in all_users]} <<<")
        
        admin_exist = db.query(models.User).filter(models.User.username == "superadmin").first()
        if not admin_exist:
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
            print(">>> STATUS: Akun Super Admin sudah tersedia (password rahasia pengguna terjaga). <<<")
    finally:
        db.close()
    yield

# 4. INISIALISASI APLIKASI FASTAPI
app = FastAPI(
    title="Borneo Agricola API",
    description="Backend Server untuk Sistem Cerdas IoT Pertanian",
    version="1.0.0",
    lifespan=lifespan
)

# Menambahkan CORS Middleware agar bisa diakses tanpa kendala blokir dari klien/web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Schema Pydantic
class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: str
    role: str 
    pembuat_id: int

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

class PumpControl(BaseModel):
    zone_id: int
    status_pompa: str
    dipicu_oleh: str

class ZoneCreate(BaseModel):
    nama_zona: str
    deskripsi: str = ""
    mac_address: str
    batas_bawah: float = 40.0
    batas_atas: float = 80.0

class ZoneUpdate(BaseModel):
    nama_zona: Optional[str] = None
    deskripsi: Optional[str] = None
    mac_address: Optional[str] = None
    batas_bawah: Optional[float] = None
    batas_atas: Optional[float] = None

class LoginRequest(BaseModel):
    username: str
    password: str

# 6. RUTE PENGUJIAN AWAL
@app.get("/")
def ping_server():
    return {"status": "sukses", "pesan": "Mesin Utama Borneo Agricola Berjalan Sempurna!"}

# 7. RUTE LOGIN (BARU DITAMBAHKAN)
@app.post("/api/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    username = req.username.strip()
    password = req.password.strip()
    print(f"\n>>> [LOGIN ATTEMPT] Menerima request login - Username: '{username}', Password: '{password}'")
    
    # Pencarian case-insensitive (mengabaikan huruf besar/kecil seperti Superadmin vs superadmin)
    user = db.query(models.User).filter(models.User.username.ilike(username)).first()
    
    if not user:
        print(f">>> [LOGIN GAGAL] Username '{username}' tidak ditemukan di database!")
        raise HTTPException(status_code=401, detail="Username atau password salah")
        
    # Cek verifikasi bcrypt ATAU plain text (jika sempat terubah manual di XAMPP)
    is_valid = False
    try:
        if pwd_context.verify(password, user.password_hash):
            is_valid = True
    except Exception:
        pass
    if not is_valid and user.password_hash == password:
        is_valid = True
        
    if not is_valid:
        print(f">>> [LOGIN GAGAL] Password salah untuk user '{user.username}'! Yang dikirim: '{password}'")
        raise HTTPException(status_code=401, detail="Username atau password salah")
        
    print(f">>> [LOGIN SUKSES] Berhasil login sebagai '{user.username}' (Role: {user.role})")
    access_token = auth.create_access_token(
        data={"sub": user.username, "role": user.role, "user_id": user.id}
    )
    return {
        "message": "Login berhasil!",
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role,
        "username": user.username
    }

# 8. RUTE PEMBUATAN AKUN & KONTROL POMPA (TERKUNCI: ADMIN ONLY)
@app.post("/api/users/create")
def create_new_user(user: UserCreate, db: Session = Depends(get_db), current_admin: models.User = Depends(auth.require_admin_role)):
    cek_user = db.query(models.User).filter(models.User.username == user.username).first()
    if cek_user:
        raise HTTPException(status_code=400, detail="Username sudah terdaftar!")
    if user.email and user.email.strip():
        cek_email = db.query(models.User).filter(models.User.email == user.email.strip()).first()
        if cek_email:
            raise HTTPException(status_code=400, detail="Email sudah terdaftar!")

    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email.strip() if user.email else None, password_hash=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    log_aksi = f"Mendaftarkan akun baru dengan username: {user.username} (Email: {user.email or 'Tidak ada'})"
    db_log = models.UserLog(user_id=user.pembuat_id, action=log_aksi)
    db.add(db_log)
    db.commit()
    return {"message": "Akun berhasil dibuat", "user_id": db_user.id}

@app.post("/api/users/change-password")
def change_user_password(req: PasswordChange, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    user_in_db = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user_in_db:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan di database.")

    is_valid = False
    try:
        if pwd_context.verify(req.old_password, user_in_db.password_hash):
            is_valid = True
    except Exception:
        pass
    if not is_valid and user_in_db.password_hash == req.old_password:
        is_valid = True

    if not is_valid:
        raise HTTPException(status_code=400, detail="Password lama salah! Mohon periksa kembali password lama Anda.")

    user_in_db.password_hash = get_password_hash(req.new_password)
    db.commit()
    db.refresh(user_in_db)
    print(f"\n>>> [GANTI PASSWORD SUKSES] Password untuk user '{user_in_db.username}' telah diperbarui di database.")
    return {"message": "Password berhasil diperbarui secara rahasia!"}

@app.post("/api/pump/control")
def control_pump(req: PumpControl, db: Session = Depends(get_db), current_admin: models.User = Depends(auth.require_admin_role)):
    topik_tujuan = f"borneo/zona-{req.zone_id}/pompa"
    sukses_terkirim = mqtt.publish_command(topic=topik_tujuan, payload=req.status_pompa)
    if not sukses_terkirim:
        raise HTTPException(status_code=500, detail="Gagal mengirim instruksi ke perangkat.")

    db_log = models.PumpLog(zone_id=req.zone_id, status_pompa=req.status_pompa, dipicu_oleh=req.dipicu_oleh)
    db.add(db_log)
    db.commit()
    return {"message": f"Instruksi {req.status_pompa} berhasil dikirim"}

# 9. RUTE DASHBOARD MOBILE (TERBUKA UNTUK ADMIN & VIEWER BERTOKEN VALID)
@app.get("/api/zones/{zone_id}/sensor/latest")
def get_latest_sensor_data(zone_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    data = db.query(models.SensorData).filter(models.SensorData.zone_id == zone_id).order_by(models.SensorData.waktu_rekam.desc()).first()
    if not data: raise HTTPException(status_code=404, detail="Data tidak ditemukan")
    return data

@app.get("/api/zones/{zone_id}/sensor/history")
def get_sensor_history(zone_id: int, limit: int = 20, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    records = db.query(models.SensorData).filter(models.SensorData.zone_id == zone_id).order_by(models.SensorData.waktu_rekam.desc()).limit(limit).all()
    return list(reversed(records))

@app.get("/api/zones/{zone_id}/pump/logs")
def get_pump_logs_history(zone_id: int, limit: int = 10, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.PumpLog).filter(models.PumpLog.zone_id == zone_id).order_by(models.PumpLog.waktu_kejadian.desc()).limit(limit).all()

@app.get("/api/zones")
def get_all_registered_zones(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Zone).all()

# 10. RUTE TAMBAH ZONA BARU (TERKUNCI: ADMIN ONLY - REVISI SEMPRO)
@app.post("/api/zones/create")
def create_new_zone(zone: ZoneCreate, db: Session = Depends(get_db), current_admin: models.User = Depends(auth.require_admin_role)):
    mac = zone.mac_address.strip().upper()
    if not mac:
        raise HTTPException(status_code=400, detail="MAC Address perangkat tidak boleh kosong!")
        
    cek_mac = db.query(models.Zone).filter(models.Zone.mac_address == mac).first()
    if cek_mac:
        raise HTTPException(status_code=400, detail=f"Perangkat dengan MAC Address '{mac}' sudah terdaftar di zona: '{cek_mac.nama_zona}'!")
        
    db_zone = models.Zone(
        nama_zona=zone.nama_zona.strip(),
        deskripsi=zone.deskripsi.strip(),
        mac_address=mac,
        batas_bawah=zone.batas_bawah,
        batas_atas=zone.batas_atas
    )
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    print(f"\n>>> [ZONA BARU DITAWARKAN] Sukses mendaftarkan '{db_zone.nama_zona}' (MAC: {mac}, Batas: {db_zone.batas_bawah}% - {db_zone.batas_atas}%)")
    return {"message": "Zona baru berhasil ditambahkan!", "zone_id": db_zone.id, "mac_address": mac}

# 11. RUTE INFORMASI & UPDATE ZONA (REVISI SEMPRO - MENGUBAH THRESHOLD PER ZONA)
@app.get("/api/zones/{zone_id}")
def get_zone_by_id(zone_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    zone = db.query(models.Zone).filter(models.Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zona tidak ditemukan!")
    return zone

@app.put("/api/zones/{zone_id}")
def update_zone_config(zone_id: int, req: ZoneUpdate, db: Session = Depends(get_db), current_admin: models.User = Depends(auth.require_admin_role)):
    db_zone = db.query(models.Zone).filter(models.Zone.id == zone_id).first()
    if not db_zone:
        raise HTTPException(status_code=404, detail="Zona tidak ditemukan!")
    
    if req.nama_zona is not None: db_zone.nama_zona = req.nama_zona.strip()
    if req.deskripsi is not None: db_zone.deskripsi = req.deskripsi.strip()
    if req.mac_address is not None and req.mac_address.strip():
        mac = req.mac_address.strip().upper()
        cek_mac = db.query(models.Zone).filter(models.Zone.mac_address == mac, models.Zone.id != zone_id).first()
        if cek_mac:
            raise HTTPException(status_code=400, detail=f"MAC Address '{mac}' sudah dipakai oleh zona lain!")
        db_zone.mac_address = mac
    if req.batas_bawah is not None: db_zone.batas_bawah = req.batas_bawah
    if req.batas_atas is not None: db_zone.batas_atas = req.batas_atas
    
    db.commit()
    db.refresh(db_zone)
    print(f"\n>>> [ZONA DIPERBARUI] Zona {zone_id} ('{db_zone.nama_zona}') - Batas Baru: {db_zone.batas_bawah}% - {db_zone.batas_atas}%")
    return {"message": "Pengaturan threshold zona berhasil diperbarui!", "zone": db_zone}

# 12. RUTE NOTIFIKASI & PERINGATAN DINI (SARAN 2 - SMART ALERTING SYSTEM)
@app.get("/api/zones/{zone_id}/alerts")
def get_zone_alerts(zone_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    zone = db.query(models.Zone).filter(models.Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zona tidak ditemukan!")
    
    latest_sensor = db.query(models.SensorData).filter(models.SensorData.zone_id == zone_id).order_by(models.SensorData.id.desc()).first()
    latest_pump_log = db.query(models.PumpLog).filter(models.PumpLog.zone_id == zone_id).order_by(models.PumpLog.id.desc()).first()
    
    alerts = []
    if latest_sensor:
        if latest_sensor.kelembapan_tanah < zone.batas_bawah:
            alerts.append({
                "severity": "CRITICAL",
                "title": "DARURAT: Tanah Terlalu Kering!",
                "message": f"Kelembapan tanah saat ini {latest_sensor.kelembapan_tanah}% berada di bawah batas minimal ({zone.batas_bawah}%). Pompa otomatis diinstruksikan ON.",
                "timestamp": str(latest_sensor.waktu_rekam)
            })
        elif latest_sensor.kelembapan_tanah > zone.batas_atas:
            alerts.append({
                "severity": "INFO",
                "title": "Tanah Lembap & Jenuh Air",
                "message": f"Kelembapan tanah mencapai {latest_sensor.kelembapan_tanah}% melebihi batas atas ({zone.batas_atas}%). Pompa dimatikan.",
                "timestamp": str(latest_sensor.waktu_rekam)
            })
        else:
            alerts.append({
                "severity": "SAFE",
                "title": "Kondisi Lahan Ideal & Stabil",
                "message": f"Kelembapan tanah {latest_sensor.kelembapan_tanah}% berada pada rentang optimal ({zone.batas_bawah}% - {zone.batas_atas}%).",
                "timestamp": str(latest_sensor.waktu_rekam)
            })
        
        if latest_sensor.suhu_udara and latest_sensor.suhu_udara > 33.0:
            alerts.append({
                "severity": "WARNING",
                "title": "Peringatan Suhu Udara Panas!",
                "message": f"Suhu udara terdeteksi {latest_sensor.suhu_udara}°C. Waspadai laju penguapan air berlebih pada zona ini.",
                "timestamp": str(latest_sensor.waktu_rekam)
            })
        if latest_sensor.status_hujan:
            alerts.append({
                "severity": "INFO",
                "title": "Sensor Hujan Aktif",
                "message": "Terdeteksi curah hujan di area lahan pertanian. Sistem irigasi diistirahatkan menghemat air.",
                "timestamp": str(latest_sensor.waktu_rekam)
            })

    if latest_pump_log:
        alerts.append({
            "severity": "INFO",
            "title": f"Aktivitas Pompa: {latest_pump_log.status_pompa}",
            "message": f"Instruksi pompa terakhir dipicu oleh: {latest_pump_log.dipicu_oleh}.",
            "timestamp": str(latest_pump_log.waktu_kejadian)
        })
        
    return {"zone_id": zone_id, "nama_zona": zone.nama_zona, "alerts": alerts}

# 13. RUTE EKSPOR LAPORAN PANEN DAN DATA SENSOR (SARAN 3 - CSV EXPORT)
@app.get("/api/zones/{zone_id}/export/sensor")
def export_sensor_data(zone_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    zone = db.query(models.Zone).filter(models.Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zona tidak ditemukan!")
        
    records = db.query(models.SensorData).filter(models.SensorData.zone_id == zone_id).order_by(models.SensorData.id.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID Rekam", "Waktu Kejadian", "Kelembapan Tanah (%)", "Suhu Udara (C)", "Kelembapan Udara (%)", "pH Tanah", "Intensitas Cahaya", "Status Hujan"])
    
    for r in records:
        writer.writerow([
            r.id,
            str(r.waktu_rekam),
            r.kelembapan_tanah,
            r.suhu_udara or 0.0,
            r.kelembapan_udara or 0.0,
            r.ph_tanah or 0.0,
            r.intensitas_cahaya or 0,
            "Ya" if r.status_hujan else "Tidak"
        ])
        
    output.seek(0)
    filename = f"laporan_sensor_zona_{zone_id}.csv"
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return StreamingResponse(output, media_type="text/csv", headers=headers)