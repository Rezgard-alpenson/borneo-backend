from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas import BaseResponse, LoginRequest, LoginResponse
from app import auth as auth_module
from app.services import user_service
from app.utils.response import ok

router = APIRouter(tags=["Authentication"])


@router.post("/api/login", response_model=BaseResponse[LoginResponse])
def login(req: LoginRequest, db: Session = Depends(get_db)):
    username = req.username.strip()
    password = req.password.strip()

    user = user_service.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=401, detail="Username atau password salah")

    if not user_service.verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Username atau password salah")

    access_token = auth_module.create_access_token(
        data={"sub": user.username, "role": user.role, "user_id": user.id}
    )
    return ok(
        data=LoginResponse(
            access_token=access_token,
            user_id=user.id,
            role=user.role,
            username=user.username,
        ),
        message="Login berhasil!",
    )
