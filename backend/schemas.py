from datetime import date, datetime
from typing import Optional, List
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
    worker_id_hash: Optional[str] = Field(None, min_length=64, max_length=64)
    daily_wage_rate: float = Field(..., gt=0)
    duration_days: int = Field(..., gt=0)
    trade: str = Field(..., max_length=100)
    site_location: str = Field(..., max_length=255)
    site_latitude: Optional[float] = None
    site_longitude: Optional[float] = None
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


# Core Operational Schemas
class DailyCheckinRequest(BaseModel):
    worker_id_hash: str = Field(..., min_length=64, max_length=64, description="SHA-256 identity hash of the worker")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Precise current GPS latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Precise current GPS longitude")
    facial_liveness_pass: bool = Field(default=True, description="Facial liveness verification flag from NPU/client")
    contract_id: Optional[int] = Field(None, description="Optional specific contract ID to validate against")
    max_distance_meters: Optional[float] = Field(default=1500.0, description="Maximum allowed distance from site in meters (geofence tolerance)")


class DailyCheckinResponse(BaseModel):
    status: str
    message: str
    worker_name: str
    worker_id_hash: str
    site_location: str
    distance_meters: Optional[float] = None
    attendance_id: int
    check_in_timestamp: datetime
    gps_coordinates: str
    facial_liveness_pass: bool


class AuditPaymentRequest(BaseModel):
    worker_id_hash: str = Field(..., min_length=64, max_length=64, description="SHA-256 identity hash of the worker")
    received_amount: float = Field(..., ge=0, description="Disbursed/incoming payment value in INR")
    contract_id: Optional[int] = Field(None, description="Optional contract ID to audit (defaults to active/latest contract)")


class AuditPaymentResponse(BaseModel):
    status: str
    wage_theft_alert: bool
    worker_id_hash: str
    worker_name: str
    contract_id: int
    contract_hash: str
    trade: str
    site_location: str
    daily_wage_rate: float
    verified_workdays: int
    expected_amount: float
    received_amount: float
    deficit: float
    message: str
    evidence_bundle: Optional[str] = None
    download_evidence_url: Optional[str] = None
