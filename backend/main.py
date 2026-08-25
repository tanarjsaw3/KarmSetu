from fastapi import FastAPI, Depends, HTTPException, status, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from database import engine, get_db, Base
import models
import schemas
from utils import (
    haversine_distance,
    extract_site_coordinates,
    generate_evidence_bundle_text
)

# Auto-create tables in SQLite database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="KarmSetu API",
    description="NPU-Driven Wage Protection & Dignity Marketplace Backend API",
    version="1.1.0"
)

# CORS Middleware
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
        "service": "KarmSetu Wage Protection Engine",
        "version": "1.1.0",
        "database": "SQLite (Local Ledger)"
    }


# ============================================================================
# 1. CORE OPERATIONAL ROUTE: /daily-checkin
# ============================================================================
@app.post(
    "/daily-checkin",
    response_model=schemas.DailyCheckinResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Core Operations"]
)
def daily_checkin(
    checkin: schemas.DailyCheckinRequest,
    db: Session = Depends(get_db)
):
    """
    Validates a worker's check-in by checking:
    1. Worker SHA-256 ID registration
    2. Active contract association
    3. Facial liveness biometric verification flag
    4. Geofence proximity to the locked contract site location
    Records a verified workday entry into the SQLite Attendance table upon passing.
    """
    # 1. Look up worker by SHA-256 ID hash
    worker = db.query(models.Worker).filter(models.Worker.id_hash == checkin.worker_id_hash).first()
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Worker with ID hash '{checkin.worker_id_hash}' not found in registry."
        )

    # 2. Look up contract for this worker
    contract_query = db.query(models.Contract)
    if checkin.contract_id:
        contract = contract_query.filter(models.Contract.id == checkin.contract_id).first()
    else:
        # Match by worker_id_hash or worker_name
        contract = contract_query.filter(
            (models.Contract.worker_id_hash == worker.id_hash) |
            (models.Contract.worker_name == worker.worker_name)
        ).order_by(models.Contract.id.desc()).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active locked contract found for worker '{worker.worker_name}'."
        )

    # 3. Verify Facial Liveness pass flag
    if not checkin.facial_liveness_pass:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Facial liveness verification failed. Daily check-in rejected."
        )

    # 4. Location Verification / Geofence Check against locked contract site
    site_coords = extract_site_coordinates(
        contract.site_location,
        contract.site_latitude,
        contract.site_longitude
    )

    distance_m = None
    if site_coords:
        site_lat, site_lon = site_coords
        distance_m = haversine_distance(checkin.latitude, checkin.longitude, site_lat, site_lon)
        max_allowed = checkin.max_distance_meters or 1500.0

        if distance_m > max_allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Geofence violation: Worker is {distance_m:.1f}m away from the locked site "
                    f"'{contract.site_location}' (Max allowed: {max_allowed:.1f}m)."
                )
            )

    # 5. Record verified attendance entry into SQLite database
    now_utc = datetime.now(timezone.utc)
    gps_str = f"{checkin.latitude:.6f}, {checkin.longitude:.6f}"

    new_attendance = models.Attendance(
        worker_id_hash=worker.id_hash,
        check_in_timestamp=now_utc,
        latitude=checkin.latitude,
        longitude=checkin.longitude,
        gps_coordinates=gps_str,
        facial_liveness_pass=True
    )
    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)

    dist_msg = f" (Distance to site: {distance_m:.1f}m)" if distance_m is not None else ""

    return schemas.DailyCheckinResponse(
        status="VERIFIED_CHECKIN",
        message=f"Workday successfully verified and logged into SQLite ledger{dist_msg}.",
        worker_name=worker.worker_name,
        worker_id_hash=worker.id_hash,
        site_location=contract.site_location,
        distance_meters=round(distance_m, 2) if distance_m is not None else None,
        attendance_id=new_attendance.id,
        check_in_timestamp=new_attendance.check_in_timestamp,
        gps_coordinates=gps_str,
        facial_liveness_pass=True
    )


# ============================================================================
# 2. CORE OPERATIONAL ROUTE: /audit-payment
# ============================================================================
@app.post(
    "/audit-payment",
    response_model=schemas.AuditPaymentResponse,
    status_code=status.HTTP_200_OK,
    tags=["Core Operations"]
)
def audit_payment(
    audit: schemas.AuditPaymentRequest,
    db: Session = Depends(get_db)
):
    """
    Audits an incoming payment against verified workdays and locked contract terms:
    1. Fetches worker and active contract details.
    2. Counts total verified attendance workdays from SQLite.
    3. Calculates Expected Funds = Verified Workdays × Daily Rate.
    4. Detects deficit = Expected Funds - Received Amount.
    5. If deficit > 0: Triggers 'Wage Theft Alert' and compiles a full text evidence bundle.
    """
    # 1. Look up worker by SHA-256 ID hash
    worker = db.query(models.Worker).filter(models.Worker.id_hash == audit.worker_id_hash).first()
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Worker with ID hash '{audit.worker_id_hash}' not found."
        )

    # 2. Fetch contract details
    contract_query = db.query(models.Contract)
    if audit.contract_id:
        contract = contract_query.filter(models.Contract.id == audit.contract_id).first()
    else:
        contract = contract_query.filter(
            (models.Contract.worker_id_hash == worker.id_hash) |
            (models.Contract.worker_name == worker.worker_name)
        ).order_by(models.Contract.id.desc()).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No contract found for worker '{worker.worker_name}' to perform wage audit."
        )

    # 3. Query all verified attendance entries for this worker
    attendance_records = db.query(models.Attendance).filter(
        models.Attendance.worker_id_hash == worker.id_hash,
        models.Attendance.facial_liveness_pass == True
    ).order_by(models.Attendance.check_in_timestamp.asc()).all()

    verified_workdays = len(attendance_records)
    daily_rate = contract.daily_wage_rate
    expected_amount = round(verified_workdays * daily_rate, 2)
    received_amount = round(audit.received_amount, 2)
    deficit = round(max(0.0, expected_amount - received_amount), 2)

    # Serialize attendance logs for evidence compilation
    attendance_logs = [
        {
            "id": att.id,
            "check_in_timestamp": att.check_in_timestamp.strftime("%Y-%m-%d %H:%M:%S UTC") if att.check_in_timestamp else "N/A",
            "latitude": att.latitude,
            "longitude": att.longitude,
            "gps_coordinates": att.gps_coordinates,
            "facial_liveness_pass": att.facial_liveness_pass
        }
        for att in attendance_records
    ]

    wage_theft_alert = deficit > 0
    evidence_bundle = None
    download_url = None

    if wage_theft_alert:
        status_label = "WAGE_THEFT_ALERT"
        message = (
            f"🚨 WAGE THEFT ALERT: Financial deficit of INR {deficit:,.2f} detected! "
            f"Expected INR {expected_amount:,.2f} for {verified_workdays} verified workdays, "
            f"but received only INR {received_amount:,.2f}."
        )
        # Compile complete downloadable text evidence bundle
        evidence_bundle = generate_evidence_bundle_text(
            worker_id_hash=worker.id_hash,
            worker_name=worker.worker_name,
            contract_hash=contract.contract_hash,
            contract_id=contract.id,
            trade=contract.trade,
            site_location=contract.site_location,
            daily_wage_rate=daily_rate,
            duration_days=contract.duration_days,
            verified_workdays=verified_workdays,
            expected_amount=expected_amount,
            received_amount=received_amount,
            deficit=deficit,
            attendance_records=attendance_logs
        )
        download_url = f"/audit-payment/download-evidence?worker_id_hash={worker.id_hash}&received_amount={received_amount}&contract_id={contract.id}"
    else:
        status_label = "VERIFIED_COMPLIANT"
        message = (
            f"Payment fully verified. Disbursed INR {received_amount:,.2f} matches or exceeds "
            f"expected INR {expected_amount:,.2f} ({verified_workdays} workdays @ INR {daily_rate:,.2f}/day)."
        )

    return schemas.AuditPaymentResponse(
        status=status_label,
        wage_theft_alert=wage_theft_alert,
        worker_id_hash=worker.id_hash,
        worker_name=worker.worker_name,
        contract_id=contract.id,
        contract_hash=contract.contract_hash,
        trade=contract.trade,
        site_location=contract.site_location,
        daily_wage_rate=daily_rate,
        verified_workdays=verified_workdays,
        expected_amount=expected_amount,
        received_amount=received_amount,
        deficit=deficit,
        message=message,
        evidence_bundle=evidence_bundle,
        download_evidence_url=download_url
    )


# ============================================================================
# DOWNLOADABLE EVIDENCE BUNDLE FILE ENDPOINT
# ============================================================================
@app.get(
    "/audit-payment/download-evidence",
    response_class=PlainTextResponse,
    tags=["Core Operations"]
)
def download_evidence_bundle(
    worker_id_hash: str = Query(..., description="Worker SHA-256 ID hash"),
    received_amount: float = Query(..., ge=0, description="Disbursed payment amount"),
    contract_id: Optional[int] = Query(None, description="Optional contract ID"),
    db: Session = Depends(get_db)
):
    """
    Directly returns the compiled Wage Theft Evidence Bundle as a downloadable text file (.txt).
    """
    worker = db.query(models.Worker).filter(models.Worker.id_hash == worker_id_hash).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    contract_query = db.query(models.Contract)
    if contract_id:
        contract = contract_query.filter(models.Contract.id == contract_id).first()
    else:
        contract = contract_query.filter(
            (models.Contract.worker_id_hash == worker.id_hash) |
            (models.Contract.worker_name == worker.worker_name)
        ).order_by(models.Contract.id.desc()).first()

    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    attendance_records = db.query(models.Attendance).filter(
        models.Attendance.worker_id_hash == worker.id_hash,
        models.Attendance.facial_liveness_pass == True
    ).order_by(models.Attendance.check_in_timestamp.asc()).all()

    verified_workdays = len(attendance_records)
    daily_rate = contract.daily_wage_rate
    expected_amount = round(verified_workdays * daily_rate, 2)
    deficit = round(max(0.0, expected_amount - received_amount), 2)

    attendance_logs = [
        {
            "id": att.id,
            "check_in_timestamp": att.check_in_timestamp.strftime("%Y-%m-%d %H:%M:%S UTC") if att.check_in_timestamp else "N/A",
            "latitude": att.latitude,
            "longitude": att.longitude,
            "gps_coordinates": att.gps_coordinates,
            "facial_liveness_pass": att.facial_liveness_pass
        }
        for att in attendance_records
    ]

    bundle_text = generate_evidence_bundle_text(
        worker_id_hash=worker.id_hash,
        worker_name=worker.worker_name,
        contract_hash=contract.contract_hash,
        contract_id=contract.id,
        trade=contract.trade,
        site_location=contract.site_location,
        daily_wage_rate=daily_rate,
        duration_days=contract.duration_days,
        verified_workdays=verified_workdays,
        expected_amount=expected_amount,
        received_amount=received_amount,
        deficit=deficit,
        attendance_records=attendance_logs
    )

    filename = f"wage_theft_evidence_{worker.worker_name.replace(' ', '_')}_{worker_id_hash[:8]}.txt"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }
    return PlainTextResponse(content=bundle_text, headers=headers)


# ============================================================================
# STANDARD CRUD ENDPOINTS (Workers, Contracts, Attendance)
# ============================================================================
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


@app.post("/contracts", response_model=schemas.ContractResponse, status_code=status.HTTP_201_CREATED, tags=["Contracts"])
def create_contract(contract: schemas.ContractCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Contract).filter(models.Contract.contract_hash == contract.contract_hash).first()
    if existing:
        raise HTTPException(status_code=400, detail="Contract with this locked hash already exists")
    db_contract = models.Contract(
        worker_name=contract.worker_name,
        worker_id_hash=contract.worker_id_hash,
        daily_wage_rate=contract.daily_wage_rate,
        duration_days=contract.duration_days,
        trade=contract.trade,
        site_location=contract.site_location,
        site_latitude=contract.site_latitude,
        site_longitude=contract.site_longitude,
        contract_hash=contract.contract_hash
    )
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract


@app.get("/contracts", response_model=List[schemas.ContractResponse], tags=["Contracts"])
def list_contracts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Contract).offset(skip).limit(limit).all()


@app.get("/attendance", response_model=List[schemas.AttendanceResponse], tags=["Attendance"])
def list_attendance(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Attendance).offset(skip).limit(limit).all()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
