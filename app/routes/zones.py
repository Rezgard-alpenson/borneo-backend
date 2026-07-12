from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas import (
    BaseResponse,
    ZoneCreate,
    ZoneUpdate,
    ZoneResponse,
    ZoneAlertsResponse,
    AlertItem,
    CreateZoneResponse,
    UpdateZoneResponse,
)
from app import models
from app.auth import get_current_user, require_admin_role
from app.services import zone_service, sensor_service, alert_service, export_service, pump_log_service
from app.services.zone_service import normalize_mac_address
from app.utils.response import ok

router = APIRouter(tags=["Zones"])


@router.get("/api/zones", response_model=BaseResponse[list[ZoneResponse]])
def get_all_registered_zones(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    zones = zone_service.get_all_zones(db)
    return ok(
        data=[ZoneResponse.model_validate(z) for z in zones],
        message="Data zona berhasil diambil",
        meta={"total": len(zones)},
    )


@router.post("/api/zones/create", response_model=BaseResponse[CreateZoneResponse])
def create_new_zone(
    zone: ZoneCreate,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(require_admin_role),
):
    mac = normalize_mac_address(zone.mac_address)
    if not mac:
        raise HTTPException(status_code=400, detail="MAC Address perangkat tidak boleh kosong!")

    if zone_service.get_zone_by_mac(db, mac):
        raise HTTPException(status_code=400, detail=f"Perangkat dengan MAC Address '{mac}' sudah terdaftar!")

    db_zone = zone_service.create_zone(
        db,
        nama_zona=zone.nama_zona,
        deskripsi=zone.deskripsi,
        mac_address=mac,
        batas_bawah=zone.batas_bawah,
        batas_atas=zone.batas_atas,
    )
    return ok(
        data=CreateZoneResponse(
            message="Zona baru berhasil ditambahkan!",
            zone_id=db_zone.id,
            mac_address=mac,
        )
    )


@router.get("/api/zones/{zone_id}", response_model=BaseResponse[ZoneResponse])
def get_zone_by_id(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    zone = zone_service.get_zone_by_id(db, zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zona tidak ditemukan!")
    return ok(data=ZoneResponse.model_validate(zone), message="Data zona berhasil diambil")


@router.put("/api/zones/{zone_id}", response_model=BaseResponse[UpdateZoneResponse])
def update_zone_config(
    zone_id: int,
    req: ZoneUpdate,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(require_admin_role),
):
    db_zone = zone_service.get_zone_by_id(db, zone_id)
    if not db_zone:
        raise HTTPException(status_code=404, detail="Zona tidak ditemukan!")

    if req.mac_address and req.mac_address.strip():
        mac = normalize_mac_address(req.mac_address)
        existing = zone_service.get_zone_by_mac(db, mac)
        if existing and existing.id != zone_id:
            raise HTTPException(status_code=400, detail=f"MAC Address '{mac}' sudah dipakai oleh zona lain!")

    db_zone = zone_service.update_zone(
        db,
        db_zone,
        nama_zona=req.nama_zona,
        deskripsi=req.deskripsi,
        mac_address=req.mac_address,
        batas_bawah=req.batas_bawah,
        batas_atas=req.batas_atas,
    )
    return ok(
        data=UpdateZoneResponse(
            message="Pengaturan threshold zona berhasil diperbarui!",
            zone=ZoneResponse.model_validate(db_zone),
        )
    )


@router.get("/api/zones/{zone_id}/alerts", response_model=BaseResponse[ZoneAlertsResponse])
def get_zone_alerts(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    zone = zone_service.get_zone_by_id(db, zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zona tidak ditemukan!")

    latest_sensor = sensor_service.get_latest_sensor_data(db, zone_id)
    pump_logs = pump_log_service.get_latest_pump_log(db, zone_id)
    alerts = alert_service.generate_alerts_for_zone(zone, latest_sensor, pump_logs)
    return ok(
        data=ZoneAlertsResponse(
            zone_id=zone_id,
            nama_zona=zone.nama_zona,
            alerts=[AlertItem(**a) for a in alerts],
        ),
        message="Data alert zona berhasil diambil",
    )


@router.get("/api/zones/{zone_id}/export/sensor")
def export_sensor_data(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    zone = zone_service.get_zone_by_id(db, zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zona tidak ditemukan!")

    filename, csv_content = export_service.export_sensor_data_csv(db, zone_id)
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers=headers,
    )
