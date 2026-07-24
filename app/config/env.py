import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()


class Settings:
    database_url: str = os.getenv("DATABASE_URL", "mysql+pymysql://root:@host.docker.internal:3306/db_borneo")
    mqtt_broker: str = os.getenv("MQTT_BROKER", "mqtt_broker")
    mqtt_port: int = int(os.getenv("MQTT_PORT", "1883"))
    mqtt_username: str = os.getenv("MQTT_USERNAME", "borneo_backend")
    mqtt_password: str = os.getenv("MQTT_PASSWORD", "")
    mqtt_retry_count: int = int(os.getenv("MQTT_RETRY_COUNT", "5"))
    mqtt_retry_delay: int = int(os.getenv("MQTT_RETRY_DELAY", "3"))
    mqtt_client_id: str = "Borneo_Backend_Server"
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "borneo_agricola_super_secret_jwt_key_2026_wicida")
    jwt_algorithm: str = "HS256"
    access_token_expire_days: int = 7


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
