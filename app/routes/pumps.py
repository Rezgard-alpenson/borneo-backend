from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas import BaseResponse, PumpControl, PumpControlResponse
from app import models, mqtt
from app.auth import require_admin_role
from app.services import pump_log_service
from app.utils.response import ok

router = APIRouter(tags=["Pumps"])


@router.post("/api/pump/control", response_model=BaseResponse[PumpControlResponse])
def control_pump(
    req: PumpControl,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(require_admin_role),
):
    topik_tujuan = f"borneo/zona-{req.zone_id}/pompa"
    sukses_terkirim = mqtt.publish_command(topic=topik_tujuan, payload=req.status_pompa)

    if not sukses_terkirim:
        raise HTTPException(status_code=500, detail="Gagal mengirim instruksi ke perangkat.")

    pump_log_service.create_pump_log(db, req.zone_id, req.status_pompa, req.dipicu_oleh)

    return ok(
        data=PumpControlResponse(
            message=f"Instruksi {req.status_pompa} berhasil dikirim",
            topik=topik_tujuan,
        )
    )
