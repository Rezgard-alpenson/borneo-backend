from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.config.database import Base


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"))
    kelembapan_tanah = Column(Float, nullable=False)
    suhu_udara = Column(Float, nullable=True)
    kelembapan_udara = Column(Float, nullable=True)
    ph_tanah = Column(Float, nullable=True)
    intensitas_cahaya = Column(Integer, nullable=True)
    status_hujan = Column(Boolean, default=False)
    debit_air = Column(Float, default=0.0)
    waktu_rekam = Column(DateTime(timezone=True), server_default=func.now())

    zone = relationship("Zone", back_populates="sensor_records")
