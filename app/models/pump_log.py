from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.config.database import Base


class PumpLog(Base):
    __tablename__ = "pump_logs"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"))
    status_pompa = Column(String(10))
    dipicu_oleh = Column(String(50))
    waktu_kejadian = Column(DateTime(timezone=True), server_default=func.now())

    zone = relationship("Zone", back_populates="pump_logs")
