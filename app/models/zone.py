from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

from app.config.database import Base


class Zone(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    nama_zona = Column(String(50), nullable=False)
    deskripsi = Column(String(255), nullable=True)
    mac_address = Column(String(50), nullable=True)
    batas_bawah = Column(Float, default=40.0)
    batas_atas = Column(Float, default=80.0)

    sensor_records = relationship("SensorData", back_populates="zone")
    pump_logs = relationship("PumpLog", back_populates="zone")
