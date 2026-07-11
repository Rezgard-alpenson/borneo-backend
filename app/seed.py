from sqlalchemy import text

from app.config.database import SessionLocal
from app import models
from app.services.user_service import hash_password


def seed_database():
    db = SessionLocal()
    try:
        try:
            db.execute(text("ALTER TABLE zones ADD COLUMN mac_address VARCHAR(50);"))
            db.commit()
        except Exception:
            db.rollback()

        try:
            db.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(100);"))
            db.commit()
        except Exception:
            db.rollback()

        zona1 = db.query(models.Zone).filter(models.Zone.id == 1).first()
        if zona1 and not zona1.mac_address:
            zona1.mac_address = "ESP32-ZONA-01"
            db.commit()

        admin = db.query(models.User).filter(models.User.username == "superadmin").first()
        if not admin:
            super_admin = models.User(
                username="superadmin",
                password_hash=hash_password("admin123"),
                role="super_admin",
                is_active=True,
            )
            db.add(super_admin)
            db.commit()
            print(">>> STATUS: Akun Super Admin pertama BERHASIL diciptakan! <<<")
        print(">>> STATUS: Seed database selesai! <<<")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
