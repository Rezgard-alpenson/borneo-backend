from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas import ZoneCreate, ZoneUpdate
from app import models
from app.auth import get_current_user, require_admin_role
from app.services import zone_service, sensor_service, alert_service, export_service, pump_log_service
from app.services.zone_service import normalize_mac_address

router = APIRouter(tags=["Zones"])


@router.get("/api/zones")
def get_all_registered_zones(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return zone_service.get_all_zones(db)


@router.post("/api/zones/create")
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
    return {"message": "Zona baru berhasil ditambahkan!", "zone_id": db_zone.id, "mac_address": mac}


@router.get("/api/zones/{zone_id}")
def get_zone_by_id(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    zone = zone_service.get_zone_by_id(db, zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zona tidak ditemukan!")
    return zone


@router.put("/api/zones/{zone_id}")
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
    return {"message": "Pengaturan threshold zona berhasil diperbarui!", "zone": db_zone}


@router.get("/api/zones/{zone_id}/alerts")
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
    return {"zone_id": zone_id, "nama_zona": zone.nama_zona, "alerts": alerts}


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
