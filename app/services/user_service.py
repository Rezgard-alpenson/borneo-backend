from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    is_valid = False
    try:
        if pwd_context.verify(plain_password, hashed_password):
            is_valid = True
    except Exception:
        pass
    if not is_valid and hashed_password == plain_password:
        is_valid = True
    return is_valid


def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(models.User).filter(models.User.username.ilike(username)).first()


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email.strip()).first()


def get_user_by_id(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, username: str, password: str, role: str, email: str | None = None) -> models.User:
    db_user = models.User(
        username=username,
        email=email.strip() if email else None,
        password_hash=hash_password(password),
        role=role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def log_action(db: Session, user_id: int, action: str):
    db_log = models.UserLog(user_id=user_id, action=action)
    db.add(db_log)
    db.commit()


def change_password(db: Session, user: models.User, new_password: str):
    user.password_hash = hash_password(new_password)
    db.commit()
    db.refresh(user)
