from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base 

# 0. Tabel Pengguna (Harus di atas agar bisa dibaca oleh UserLog)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=True)
    password_hash = Column(String(255)) 
    role = Column(String(20), default="petani")
    is_active = Column(Boolean, default=True)

    # Relasi ke UserLog
    logs = relationship("UserLog", back_populates="user")

# 1. Tabel Zona (Mengelola area penyiraman dan batas kelembapan)
class Zone(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    nama_zona = Column(String(50), nullable=False) # Contoh: "Zona A - Tomat"
    deskripsi = Column(String(255), nullable=True)
    
    # --- LOGIKA KENDALI & IDENTITAS ALAT (HASIL REVISI SEMPRO) ---
    mac_address = Column(String(50), nullable=True) # MAC Address atau ID Unik ESP32 Ican
    batas_bawah = Column(Float, default=40.0) # Pompa ON jika kelembapan di bawah ini
    batas_atas = Column(Float, default=80.0)  # Pompa OFF jika kelembapan di atas ini

    # Relasi ke SensorData dan PumpLog
    sensor_records = relationship("SensorData", back_populates="zone")
    pump_logs = relationship("PumpLog", back_populates="zone")

# 2. Tabel Data Sensor (Sesuai List Sensor dari Ican)
class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id")) # Mengikat data ini ke zona tertentu
    
    # --- KONTRAK DATA SENSOR DARI ALAT ICAN ---
    kelembapan_tanah = Column(Float, nullable=False)
    suhu_udara = Column(Float, nullable=True)
    kelembapan_udara = Column(Float, nullable=True)
    ph_tanah = Column(Float, nullable=True)
    intensitas_cahaya = Column(Integer, nullable=True)
    status_hujan = Column(Boolean, default=False)
    debit_air = Column(Float, default=0.0)
    
    waktu_rekam = Column(DateTime(timezone=True), server_default=func.now()) 

    # Relasi balik ke tabel Zone
    zone = relationship("Zone", back_populates="sensor_records")

# 3. Tabel Riwayat Pompa (Mencatat kapan pompa menyala, mati, dan siapa yang menyalakan)
class PumpLog(Base):
    __tablename__ = "pump_logs"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"))
    status_pompa = Column(String(10)) # "ON" atau "OFF"
    dipicu_oleh = Column(String(50)) # "Otomatis (Sensor)" atau "Manual (Aplikasi)"
    waktu_kejadian = Column(DateTime(timezone=True), server_default=func.now())

    # Relasi balik ke tabel Zone
    zone = relationship("Zone", back_populates="pump_logs")

# 4. Tabel Riwayat Pengguna (Activity Log - CCTV Sistem)
class UserLog(Base):
    __tablename__ = "user_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # Mengaitkan log dengan ID pembuatnya
    action = Column(String(255)) 
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relasi balik ke tabel User ( Bagian yang tadi terpotong )
    user = relationship("User", back_populates="logs")