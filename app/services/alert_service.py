def generate_alerts_for_zone(zone, latest_sensor, latest_pump_log) -> list[dict]:
    alerts = []

    if latest_sensor:
        if latest_sensor.kelembapan_tanah < zone.batas_bawah:
            alerts.append({
                "severity": "CRITICAL",
                "title": "DARURAT: Tanah Terlalu Kering!",
                "message": f"Kelembapan tanah saat ini {latest_sensor.kelembapan_tanah}% berada di bawah batas minimal ({zone.batas_bawah}%). Pompa otomatis diinstruksikan ON.",
                "timestamp": str(latest_sensor.waktu_rekam),
            })
        elif latest_sensor.kelembapan_tanah > zone.batas_atas:
            alerts.append({
                "severity": "INFO",
                "title": "Tanah Lembap & Jenuh Air",
                "message": f"Kelembapan tanah mencapai {latest_sensor.kelembapan_tanah}% melebihi batas atas ({zone.batas_atas}%). Pompa dimatikan.",
                "timestamp": str(latest_sensor.waktu_rekam),
            })
        else:
            alerts.append({
                "severity": "SAFE",
                "title": "Kondisi Lahan Ideal & Stabil",
                "message": f"Kelembapan tanah {latest_sensor.kelembapan_tanah}% berada pada rentang optimal ({zone.batas_bawah}% - {zone.batas_atas}%).",
                "timestamp": str(latest_sensor.waktu_rekam),
            })

        if latest_sensor.suhu_udara and latest_sensor.suhu_udara > 33.0:
            alerts.append({
                "severity": "WARNING",
                "title": "Peringatan Suhu Udara Panas!",
                "message": f"Suhu udara terdeteksi {latest_sensor.suhu_udara}°C. Waspadai laju penguapan air berlebih pada zona ini.",
                "timestamp": str(latest_sensor.waktu_rekam),
            })

        if latest_sensor.status_hujan:
            alerts.append({
                "severity": "INFO",
                "title": "Sensor Hujan Aktif",
                "message": "Terdeteksi curah hujan di area lahan pertanian. Sistem irigasi diistirahatkan menghemat air.",
                "timestamp": str(latest_sensor.waktu_rekam),
            })

    if latest_pump_log:
        alerts.append({
            "severity": "INFO",
            "title": f"Aktivitas Pompa: {latest_pump_log.status_pompa}",
            "message": f"Instruksi pompa terakhir dipicu oleh: {latest_pump_log.dipicu_oleh}.",
            "timestamp": str(latest_pump_log.waktu_kejadian),
        })

    return alerts
