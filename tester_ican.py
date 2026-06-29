import paho.mqtt.client as mqtt
import json

# Ini adalah simulasi ESP32 yang ditanam di lahan
BROKER = "localhost" # Karena kita tes dari laptop (Windows)
PORT = 1883
TOPIK = "borneo/zona-1/sensor"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, PORT)

# Skenario: Tanah sedang SANGAT KERING (30%), di bawah batas_bawah (40%)
payload = {
    "zone_id": 1,
    "kelembapan_tanah": 30.0,  # <-- Ini yang akan memicu Pompa menyala!
    "suhu_udara": 33.5,
    "kelembapan_udara": 60.0,
    "ph_tanah": 6.5,
    "intensitas_cahaya": 800,
    "status_hujan": False,
    "debit_air": 0.0
}

pesan_json = json.dumps(payload)
print(f"Ican mengirim data ke {TOPIK}...")
client.publish(TOPIK, pesan_json)
print("Data terkirim! Cek log Docker api_borneo sekarang.")