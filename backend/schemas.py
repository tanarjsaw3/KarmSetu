from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# Worker Schemas
class WorkerBase(BaseModel):
    id_hash: str = Field(..., min_length=64, max_length=64, description="SHA-256 hash of worker identity")
    worker_name: str = Field(..., max_length=255)
    date_of_birth: date


class WorkerCreate(WorkerBase):
    pass


class WorkerResponse(WorkerBase):
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# Contract Schemas
class ContractBase(BaseModel):
    worker_name: str = Field(..., max_length=255)
    daily_wage_rate: float = Field(..., gt=0)
    duration_days: int = Field(..., gt=0)
    trade: str = Field(..., max_length=100)
    site_location: str = Field(..., max_length=255)
    contract_hash: str = Field(..., min_length=64, max_length=64, description="Locked SHA-256 hash string of contract terms")


class ContractCreate(ContractBase):
    pass


class ContractResponse(ContractBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# Attendance Schemas
class AttendanceBase(BaseModel):
    worker_id_hash: str = Field(..., min_length=64, max_length=64)
    check_in_timestamp: Optional[datetime] = None
    latitude: float
    longitude: float
    gps_coordinates: Optional[str] = None
    facial_liveness_pass: bool = False


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceResponse(AttendanceBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
