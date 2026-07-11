from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas import UserCreate, PasswordChange
from app import models
from app.auth import get_current_user, require_admin_role
from app.services import user_service

router = APIRouter(tags=["Users"])


@router.post("/api/users/create")
def create_new_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(require_admin_role),
):
    if user_service.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username sudah terdaftar!")

    if user.email and user.email.strip():
        if user_service.get_user_by_email(db, user.email):
            raise HTTPException(status_code=400, detail="Email sudah terdaftar!")

    db_user = user_service.create_user(
        db,
        username=user.username,
        password=user.password,
        role=user.role,
        email=user.email,
    )
    log_aksi = f"Mendaftarkan akun baru dengan username: {user.username} (Email: {user.email or 'Tidak ada'})"
    user_service.log_action(db, user.pembuat_id, log_aksi)
    return {"message": "Akun berhasil dibuat", "user_id": db_user.id}


@router.post("/api/users/change-password")
def change_user_password(
    req: PasswordChange,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    user_in_db = user_service.get_user_by_id(db, current_user.id)
    if not user_in_db:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan di database.")

    if not user_service.verify_password(req.old_password, user_in_db.password_hash):
        raise HTTPException(status_code=400, detail="Password lama salah! Mohon periksa kembali password lama Anda.")

    user_service.change_password(db, user_in_db, req.new_password)
    return {"message": "Password berhasil diperbarui secara rahasia!"}
