import paho.mqtt.client as mqtt
import json
from database import SessionLocal
import models

# 1. Konfigurasi Broker
BROKER_ADDRESS = "mqtt_broker" # Nanti Faidil akan mengubah ini menjadi IP VPS Wicida
PORT = 1883
CLIENT_ID = "Borneo_Backend_Server"

# 2. Inisialisasi Klien MQTT (Menggunakan versi API terbaru)
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)

# --- FUNGSI TELINGA & OTAK SERVER (SUBSCRIBER) ---

def on_connect(client, userdata, flags, reason_code, properties):
    """Dieksekusi otomatis saat server sukses berjabat tangan dengan Mosquitto"""
    if reason_code == 0:
        print(f">>> STATUS: Server berhasil terhubung ke MQTT Broker di {BROKER_ADDRESS}:{PORT} <<<")
        
        # Mamasang telinga: Berlangganan ke topik sensor dari semua zona (tanda '+' adalah wildcard)
        client.subscribe("borneo/+/sensor")
        print("[MQTT] Telinga diaktifkan: Berhasil subscribe ke topik 'borneo/+/sensor'")
    else:
        print(f">>> ERROR: Gagal terhubung dengan kode {reason_code} <<<")

def on_message(client, userdata, msg):
    """Dieksekusi otomatis setiap kali alat Ican mengirim data JSON"""
    try:
        # 1. Menerjemahkan pesan masuk
        payload = json.loads(msg.payload.decode("utf-8"))
        topik = msg.topic # Contoh: borneo/zona-1/sensor
        
        # Ekstrak angka zona dari topik (mengambil angka 1 dari 'zona-1')
        zone_id_str = topik.split("/")[1].split("-")[1] 
        zone_id = int(zone_id_str)

        print(f"\n[MQTT Masuk] Data dari Zona {zone_id} diterima: {payload}")

        # Buka koneksi database khusus untuk jalur belakang ini (Thread aman)
        db = SessionLocal()

        try:
            # 2. Cetak data sensor ke Database (Tabel SensorData)
            sensor_baru = models.SensorData(
                zone_id=zone_id,
                kelembapan_tanah=payload.get("kelembapan_tanah", 0.0),
                suhu_udara=payload.get("suhu_udara"),
                kelembapan_udara=payload.get("kelembapan_udara"),
                ph_tanah=payload.get("ph_tanah"),
                intensitas_cahaya=payload.get("intensitas_cahaya"),
                status_hujan=payload.get("status_hujan", False),
                debit_air=payload.get("debit_air", 0.0)
            )
            db.add(sensor_baru)
            db.commit()

            # 3. LOGIKA KENDALI OTOMATIS (REVISI SEMPRO)
            zona = db.query(models.Zone).filter(models.Zone.id == zone_id).first()
            if zona:
                kelembapan_saat_ini = payload.get("kelembapan_tanah", 0.0)
                topik_pompa = f"borneo/zona-{zone_id}/pompa"

                # Cek jika kelembapan anjlok di bawah batas bawah -> NYALAKAN POMPA
                if kelembapan_saat_ini < zona.batas_bawah:
                    client.publish(topik_pompa, "ON")
                    catat_riwayat_pompa(db, zone_id, "ON", "Otomatis (Threshold Bawah)")
                    print(f"  --> [AKSI] Kelembapan ({kelembapan_saat_ini}%) KERING! Pompa ON dikirim.")
                
                # Cek jika kelembapan sudah melebihi batas atas -> MATIKAN POMPA
                elif kelembapan_saat_ini > zona.batas_atas:
                    client.publish(topik_pompa, "OFF")
                    catat_riwayat_pompa(db, zone_id, "OFF", "Otomatis (Threshold Atas)")
                    print(f"  --> [AKSI] Kelembapan ({kelembapan_saat_ini}%) BASAH! Pompa OFF dikirim.")
                else:
                    print(f"  --> [AMAN] Kelembapan normal. Tidak ada aksi.")
            else:
                print(f"  --> [PERINGATAN] Zona {zone_id} tidak ditemukan di Database!")

        finally:
            db.close() # Wajib ditutup agar RAM server tidak bocor

    except Exception as e:
        print(f"[MQTT Error] Gagal memproses pesan masuk: {e}")

def catat_riwayat_pompa(db, zone_id: int, status: str, pemicu: str):
    """Fungsi bantuan untuk mencetak ke CCTV Pompa"""
    log_pompa = models.PumpLog(zone_id=zone_id, status_pompa=status, dipicu_oleh=pemicu)
    db.add(log_pompa)
    db.commit()

# Mendaftarkan fungsi telinga dan otak ke klien MQTT
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# --- FUNGSI UTAMA KONEKSI & PUBLISH (TIDAK BERUBAH) ---

def connect_mqtt():
    """Fungsi untuk menyambungkan server ke perantara pesan (Broker)"""
    try:
        mqtt_client.connect(BROKER_ADDRESS, PORT)
        mqtt_client.loop_start() # Menjalankan loop di latar belakang agar mendengarkan terus-menerus
    except Exception as e:
        print(f">>> ERROR: Gagal inisialisasi koneksi MQTT. ({e}) <<<")

def publish_command(topic: str, payload: str):
    """Fungsi untuk mengirim pesan (publish) ke ESP32 secara manual dari aplikasi"""
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