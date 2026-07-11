from sqlalchemy.orm import Session

from app import models


def get_latest_pump_log(db: Session, zone_id: int) -> models.PumpLog | None:
    return (
        db.query(models.PumpLog)
        .filter(models.PumpLog.zone_id == zone_id)
        .order_by(models.PumpLog.id.desc())
        .first()
    )


def get_pump_logs_history(db: Session, zone_id: int, limit: int = 10) -> list[models.PumpLog]:
    return (
        db.query(models.PumpLog)
        .filter(models.PumpLog.zone_id == zone_id)
        .order_by(models.PumpLog.waktu_kejadian.desc())
        .limit(limit)
        .all()
    )


def create_pump_log(db: Session, zone_id: int, status: str, pemicu: str):
    log = models.PumpLog(zone_id=zone_id, status_pompa=status, dipicu_oleh=pemicu)
    db.add(log)
    db.commit()
