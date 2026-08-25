from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Worker(Base):
    __tablename__ = "workers"

    # ID reference stored strictly as a 64-character SHA-256 hash
    id_hash = Column(String(64), primary_key=True, index=True, doc="SHA-256 hash reference of the worker identity")
    worker_name = Column(String(255), nullable=False, doc="Full name of the worker")
    date_of_birth = Column(Date, nullable=False, doc="Date of birth")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    attendances = relationship("Attendance", back_populates="worker", cascade="all, delete-orphan")
    contracts = relationship("Contract", back_populates="worker")


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    worker_id_hash = Column(String(64), ForeignKey("workers.id_hash"), nullable=True, index=True, doc="Optional direct SHA-256 reference to Worker")
    worker_name = Column(String(255), nullable=False, doc="Worker name associated with contract")
    daily_wage_rate = Column(Float, nullable=False, doc="Agreed daily wage rate in INR")
    duration_days = Column(Integer, nullable=False, doc="Duration of contract in days")
    trade = Column(String(100), nullable=False, doc="Trade/Skill specification (e.g., Mason, Carpenter, Electrician)")
    site_location = Column(String(255), nullable=False, doc="Construction/Work site location")
    site_latitude = Column(Float, nullable=True, doc="Optional target site GPS latitude")
    site_longitude = Column(Float, nullable=True, doc="Optional target site GPS longitude")
    contract_hash = Column(String(64), nullable=False, unique=True, index=True, doc="Locked SHA-256 contract hash string")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    worker = relationship("Worker", back_populates="contracts")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    worker_id_hash = Column(String(64), ForeignKey("workers.id_hash"), nullable=False, index=True, doc="SHA-256 hash reference to Worker")
    check_in_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, doc="Daily check-in timestamp")
    latitude = Column(Float, nullable=False, doc="Precise GPS latitude coordinate")
    longitude = Column(Float, nullable=False, doc="Precise GPS longitude coordinate")
    gps_coordinates = Column(String(100), nullable=False, doc="Combined precise GPS coordinate string")
    facial_liveness_pass = Column(Boolean, default=False, nullable=False, doc="Facial liveness verification pass flag")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    worker = relationship("Worker", back_populates="attendances")
