import json
import time

import paho.mqtt.client as mqtt

from app.config.env import settings
from app.config.database import SessionLocal
from app import models
from app.services import zone_service, pump_log_service

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=settings.mqtt_client_id)


def _catat_riwayat_pompa(db, zone_id: int, status: str, pemicu: str):
    pump_log_service.create_pump_log(db, zone_id, status, pemicu)


def _proses_auto_pompa(client, db, zone_id: int, zona, kelembapan_saat_ini: float):
    topik_pompa = f"borneo/zona-{zone_id}/pompa"

    if kelembapan_saat_ini < zona.batas_bawah:
        client.publish(topik_pompa, "ON")
        _catat_riwayat_pompa(db, zone_id, "ON", "Otomatis (Threshold Bawah)")
        print(f"  --> [AKSI] Kelembapan ({kelembapan_saat_ini}%) KERING! Pompa ON dikirim.")

    elif kelembapan_saat_ini > zona.batas_atas:
        client.publish(topik_pompa, "OFF")
        _catat_riwayat_pompa(db, zone_id, "OFF", "Otomatis (Threshold Atas)")
        print(f"  --> [AKSI] Kelembapan ({kelembapan_saat_ini}%) BASAH! Pompa OFF dikirim.")
    else:
        print(f"  --> [AMAN] Kelembapan normal. Tidak ada aksi.")


def _buat_atau_dapatkan_zona(db, zone_id: int):
    zona = zone_service.get_zone_by_id(db, zone_id)
    if not zona:
        zona_baru = models.Zone(
            id=zone_id,
            nama_zona=f"Zona {zone_id}",
            deskripsi=f"Zona {zone_id} - Terdaftar otomatis dari sensor",
        )
        db.add(zona_baru)
        db.commit()
        print(f"  --> [INFO] Zona {zone_id} otomatis dibuat di database!")
        zona = zona_baru
    return zona


def _simpan_data_sensor(db, zone_id: int, payload: dict):
    sensor_baru = models.SensorData(
        zone_id=zone_id,
        kelembapan_tanah=payload.get("kelembapan_tanah", 0.0),
        suhu_udara=payload.get("suhu_udara"),
        kelembapan_udara=payload.get("kelembapan_udara"),
        ph_tanah=payload.get("ph_tanah"),
        intensitas_cahaya=payload.get("intensitas_cahaya"),
        status_hujan=payload.get("status_hujan", False),
        debit_air=payload.get("debit_air", 0.0),
    )
    db.add(sensor_baru)
    db.commit()
    return sensor_baru


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f">>> STATUS: Server berhasil terhubung ke MQTT Broker di {settings.mqtt_broker}:{settings.mqtt_port} <<<")
        client.subscribe("borneo/+/sensor")
        print("[MQTT] Telinga diaktifkan: Berhasil subscribe ke topik 'borneo/+/sensor'")
    else:
        print(f">>> ERROR: Gagal terhubung dengan kode {reason_code} <<<")


def on_disconnect(client, userdata, flags, reason_code, properties):
    print(f">>> PERINGATAN: Koneksi MQTT terputus (kode {reason_code}). Mencoba reconnect... <<<")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        topik = msg.topic

        zone_id_str = topik.split("/")[1].split("-")[1]
        zone_id = int(zone_id_str)

        print(f"\n[MQTT Masuk] Data dari Zona {zone_id} diterima: {payload}")

        db = SessionLocal()
        try:
            zona = _buat_atau_dapatkan_zona(db, zone_id)
            _simpan_data_sensor(db, zone_id, payload)

            kelembapan_saat_ini = payload.get("kelembapan_tanah", 0.0)
            _proses_auto_pompa(client, db, zone_id, zona, kelembapan_saat_ini)
        finally:
            db.close()

    except Exception as e:
        print(f"[MQTT Error] Gagal memproses pesan masuk: {e}")


mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_message = on_message


def connect_mqtt():
    for percobaan in range(1, settings.mqtt_retry_count + 1):
        try:
            print(f"[MQTT] Mencoba koneksi ke {settings.mqtt_broker}:{settings.mqtt_port} (percobaan {percobaan}/{settings.mqtt_retry_count})...")
            mqtt_client.connect(settings.mqtt_broker, settings.mqtt_port)
            mqtt_client.loop_start()
            print(f">>> STATUS: Koneksi MQTT berhasil tersambung ke {settings.mqtt_broker}:{settings.mqtt_port} <<<")
            return
        except Exception as e:
            print(f">>> ERROR: Gagal inisialisasi koneksi MQTT. ({e}) <<<")
            if percobaan < settings.mqtt_retry_count:
                print(f"[MQTT] Menunggu {settings.mqtt_retry_delay} detik sebelum percobaan ulang...")
                time.sleep(settings.mqtt_retry_delay)
            else:
                print(f">>> KRITIS: Gagal terhubung setelah {settings.mqtt_retry_count} percobaan. Server tetap berjalan tanpa MQTT. <<<")


def publish_command(topic: str, payload: str) -> bool:
    try:
        result = mqtt_client.publish(topic, payload)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"[MQTT] Sukses mengirim instruksi '{payload}' ke topik '{topic}'")
            return True
        else:
            print(f"[MQTT] Gagal mengirim instruksi. Kode Error: {result.rc}")
            return False
    except Exception as e:
        print(f"[MQTT] Terjadi kesalahan sistem: {e}")
        return False
