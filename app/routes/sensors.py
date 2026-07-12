from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas import BaseResponse, SensorDataResponse, PumpLogResponse
from app import models
from app.auth import get_current_user
from app.services import sensor_service, pump_log_service
from app.utils.response import ok

router = APIRouter(tags=["Sensors"])


@router.get("/api/zones/{zone_id}/sensor/latest", response_model=BaseResponse[SensorDataResponse])
def get_latest_sensor_data(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    data = sensor_service.get_latest_sensor_data(db, zone_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Belum ada data sensor untuk Zona {zone_id}")
    return ok(data=SensorDataResponse.model_validate(data), message="Data sensor terbaru berhasil diambil")


@router.get("/api/zones/{zone_id}/sensor/history", response_model=BaseResponse[list[SensorDataResponse]])
def get_sensor_history(
    zone_id: int,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    data = sensor_service.get_sensor_history(db, zone_id, limit)
    return ok(
        data=[SensorDataResponse.model_validate(d) for d in data],
        message="Riwayat data sensor berhasil diambil",
        meta={"total": len(data), "limit": limit},
    )


@router.get("/api/zones/{zone_id}/pump/logs", response_model=BaseResponse[list[PumpLogResponse]])
def get_pump_logs_history(
    zone_id: int,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    data = pump_log_service.get_pump_logs_history(db, zone_id, limit)
    return ok(
        data=[PumpLogResponse.model_validate(d) for d in data],
        message="Riwayat log pompa berhasil diambil",
        meta={"total": len(data), "limit": limit},
    )
