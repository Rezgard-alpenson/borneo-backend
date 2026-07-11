from sqlalchemy.orm import Session

from app import models


def normalize_mac_address(mac: str) -> str:
    return mac.strip().upper()


def get_zone_by_id(db: Session, zone_id: int) -> models.Zone | None:
    return db.query(models.Zone).filter(models.Zone.id == zone_id).first()


def get_zone_by_mac(db: Session, mac_address: str) -> models.Zone | None:
    return db.query(models.Zone).filter(models.Zone.mac_address == mac_address).first()


def get_all_zones(db: Session) -> list[models.Zone]:
    return db.query(models.Zone).all()


def create_zone(
    db: Session,
    nama_zona: str,
    deskripsi: str,
    mac_address: str,
    batas_bawah: float,
    batas_atas: float,
) -> models.Zone:
    db_zone = models.Zone(
        nama_zona=nama_zona.strip(),
        deskripsi=deskripsi.strip(),
        mac_address=normalize_mac_address(mac_address),
        batas_bawah=batas_bawah,
        batas_atas=batas_atas,
    )
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    return db_zone


def update_zone(db: Session, zone: models.Zone, **kwargs):
    for key, value in kwargs.items():
        if value is not None:
            if key == "mac_address" and value.strip():
                setattr(zone, key, normalize_mac_address(value))
            elif key in ("nama_zona", "deskripsi"):
                setattr(zone, key, value.strip())
            else:
                setattr(zone, key, value)
    db.commit()
    db.refresh(zone)
    return zone
