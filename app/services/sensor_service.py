from sqlalchemy.orm import Session

from app import models


def get_latest_sensor_data(db: Session, zone_id: int) -> models.SensorData | None:
    return (
        db.query(models.SensorData)
        .filter(models.SensorData.zone_id == zone_id)
        .order_by(models.SensorData.waktu_rekam.desc())
        .first()
    )


def get_sensor_history(db: Session, zone_id: int, limit: int = 20) -> list[models.SensorData]:
    records = (
        db.query(models.SensorData)
        .filter(models.SensorData.zone_id == zone_id)
        .order_by(models.SensorData.waktu_rekam.desc())
        .limit(limit)
        .all()
    )
    return list(reversed(records))
