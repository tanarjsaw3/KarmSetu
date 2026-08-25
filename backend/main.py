from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from database import engine, get_db, Base
import models
import schemas

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="KarmSetu API",
    description="NPU-Driven Wage Protection & Dignity Marketplace Backend API",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def read_root():
    return {
        "status": "online",
        "service": "KarmSetu Wage Protection API",
        "version": "1.0.0"
    }


# Workers Endpoints
@app.post("/workers", response_model=schemas.WorkerResponse, status_code=status.HTTP_201_CREATED, tags=["Workers"])
def create_worker(worker: schemas.WorkerCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Worker).filter(models.Worker.id_hash == worker.id_hash).first()
    if existing:
        raise HTTPException(status_code=400, detail="Worker with this SHA-256 hash already registered")
    db_worker = models.Worker(
        id_hash=worker.id_hash,
        worker_name=worker.worker_name,
        date_of_birth=worker.date_of_birth
    )
    db.add(db_worker)
    db.commit()
    db.refresh(db_worker)
    return db_worker


@app.get("/workers", response_model=List[schemas.WorkerResponse], tags=["Workers"])
def list_workers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Worker).offset(skip).limit(limit).all()


# Contracts Endpoints
@app.post("/contracts", response_model=schemas.ContractResponse, status_code=status.HTTP_201_CREATED, tags=["Contracts"])
def create_contract(contract: schemas.ContractCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Contract).filter(models.Contract.contract_hash == contract.contract_hash).first()
    if existing:
        raise HTTPException(status_code=400, detail="Contract with this locked hash already exists")
    db_contract = models.Contract(
        worker_name=contract.worker_name,
        daily_wage_rate=contract.daily_wage_rate,
        duration_days=contract.duration_days,
        trade=contract.trade,
        site_location=contract.site_location,
        contract_hash=contract.contract_hash
    )
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract


@app.get("/contracts", response_model=List[schemas.ContractResponse], tags=["Contracts"])
def list_contracts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Contract).offset(skip).limit(limit).all()


# Attendance Endpoints
@app.post("/attendance", response_model=schemas.AttendanceResponse, status_code=status.HTTP_201_CREATED, tags=["Attendance"])
def record_attendance(attendance: schemas.AttendanceCreate, db: Session = Depends(get_db)):
    worker = db.query(models.Worker).filter(models.Worker.id_hash == attendance.worker_id_hash).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker ID hash not found in registered workers")

    gps_str = attendance.gps_coordinates or f"{attendance.latitude:.6f}, {attendance.longitude:.6f}"

    db_attendance = models.Attendance(
        worker_id_hash=attendance.worker_id_hash,
        latitude=attendance.latitude,
        longitude=attendance.longitude,
        gps_coordinates=gps_str,
        facial_liveness_pass=attendance.facial_liveness_pass
    )
    if attendance.check_in_timestamp:
        db_attendance.check_in_timestamp = attendance.check_in_timestamp

    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance


@app.get("/attendance", response_model=List[schemas.AttendanceResponse], tags=["Attendance"])
def list_attendance(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Attendance).offset(skip).limit(limit).all()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
