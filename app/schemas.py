from typing import Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: str
    role: str
    pembuat_id: int


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class PumpControl(BaseModel):
    zone_id: int
    status_pompa: str
    dipicu_oleh: str


class ZoneCreate(BaseModel):
    nama_zona: str
    deskripsi: str = ""
    mac_address: str
    batas_bawah: float = 40.0
    batas_atas: float = 80.0


class ZoneUpdate(BaseModel):
    nama_zona: Optional[str] = None
    deskripsi: Optional[str] = None
    mac_address: Optional[str] = None
    batas_bawah: Optional[float] = None
    batas_atas: Optional[float] = None
