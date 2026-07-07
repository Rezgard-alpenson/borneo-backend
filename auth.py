import os
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import SessionLocal, get_db
import models

# --- 1. KONFIGURASI RAHSIA JWT ---
# Mengambil kunci rahasia dari environment variable (.env) atau fallback ke kunci default yang kuat
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "borneo_agricola_super_secret_jwt_key_2026_wicida")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7  # Token berlaku 7 hari agar petani tidak perlu login setiap hari di lahan

security = HTTPBearer()

# Dependency database untuk auth (Menggunakan get_db)
def get_db_auth():
    return get_db()

# --- 2. PEMBUATAN TOKEN (ENCODE) ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Membuat JSON Web Token (JWT) yang ditandatangani secara kriptografis menggunakan HMAC-SHA256.
    Token ini menyimpan identitas dan role pengguna secara aman (tamper-proof).
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- 3. SATPAM PELADEN: VERIFIKASI IDENTITAS (GET CURRENT USER) ---
def get_current_user(
    auth_credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Mengekstrak dan memvalidasi token Bearer dari HTTP header.
    Jika tanda tangan palsu atau masa berlaku habis, langsung kembalikan HTTP 401 Unauthorized.
    """
    token = auth_credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sesi Anda telah habis atau token tidak valid. Silakan login kembali.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        print(">>> [AUTH ERROR] Token JWT telah kedaluwarsa!")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Masa berlaku sesi telah habis. Silakan login kembali.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        print(">>> [AUTH ERROR] Token JWT palsu atau rusak!")
        raise credentials_exception

    user = db.query(models.User).filter(models.User.username.ilike(username)).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Akun pengguna ini telah dinonaktifkan.")
        
    return user

# --- 4. ATURAN RBAC BORNEO AGRICOLA: KHUSUS EKSEKUTOR (ADMIN) ---
def require_admin_role(user: models.User = Depends(get_current_user)) -> models.User:
    """
    Dependency wajib untuk endpoint eksekusi hardware (MQTT) dan mutasi data (POST/PUT/DELETE).
    Menolak akses jika role pengguna adalah 'viewer' (Operator Lapangan) dengan HTTP 403 Forbidden.
    """
    if user.role not in ["admin", "super_admin"]:
        print(f">>> [RBAC BLOCKED] Pengguna '{user.username}' (Role: {user.role}) ditolak mengakses endpoint Admin!")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses Ditolak! Fitur ini khusus untuk Eksekutor (Admin / Super Admin)."
        )
    return user
