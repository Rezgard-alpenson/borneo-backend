from datetime import datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict

DataT = TypeVar("DataT")


class BaseResponse(BaseModel, Generic[DataT]):
    success: bool = True
    message: str = "Success"
    data: Optional[DataT] = None
    meta: Optional[dict] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str
    username: str


class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: str
    role: str
    pembuat_id: int


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: Optional[str] = None
    role: str


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


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


class ZoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nama_zona: str
    deskripsi: Optional[str] = None
    mac_address: Optional[str] = None
    batas_bawah: float
    batas_atas: float


class AlertItem(BaseModel):
    severity: str
    title: str
    message: str
    timestamp: str


class ZoneAlertsResponse(BaseModel):
    zone_id: int
    nama_zona: str
    alerts: list[AlertItem]


class SensorDataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    zone_id: int
    kelembapan_tanah: float
    suhu_udara: Optional[float] = None
    kelembapan_udara: Optional[float] = None
    ph_tanah: Optional[float] = None
    intensitas_cahaya: Optional[int] = None
    status_hujan: bool
    debit_air: float
    waktu_rekam: datetime


class PumpLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    zone_id: int
    status_pompa: str
    dipicu_oleh: str
    waktu_kejadian: datetime


class PumpControl(BaseModel):
    zone_id: int
    status_pompa: str
    dipicu_oleh: str


class PumpControlResponse(BaseModel):
    message: str
    topik: str


class CreateZoneResponse(BaseModel):
    message: str
    zone_id: int
    mac_address: str


class UpdateZoneResponse(BaseModel):
    message: str
    zone: ZoneResponse


class MessageResponse(BaseModel):
    message: str
