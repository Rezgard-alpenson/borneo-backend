import csv
import io

from sqlalchemy.orm import Session

from app import models


def export_sensor_data_csv(db: Session, zone_id: int) -> tuple[str, str]:
    records = (
        db.query(models.SensorData)
        .filter(models.SensorData.zone_id == zone_id)
        .order_by(models.SensorData.id.desc())
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID Rekam",
        "Waktu Kejadian",
        "Kelembapan Tanah (%)",
        "Suhu Udara (C)",
        "Kelembapan Udara (%)",
        "pH Tanah",
        "Intensitas Cahaya",
        "Status Hujan",
    ])

    for r in records:
        writer.writerow([
            r.id,
            str(r.waktu_rekam),
            r.kelembapan_tanah,
            r.suhu_udara or 0.0,
            r.kelembapan_udara or 0.0,
            r.ph_tanah or 0.0,
            r.intensitas_cahaya or 0,
            "Ya" if r.status_hujan else "Tidak",
        ])

    output.seek(0)
    filename = f"laporan_sensor_zona_{zone_id}.csv"
    return filename, output.getvalue()
