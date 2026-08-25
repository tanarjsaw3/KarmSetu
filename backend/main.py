import os
import re
import json
import hashlib
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from database import engine, get_db, Base
import models
import schemas
from utils import (
    haversine_distance,
    extract_site_coordinates,
    generate_evidence_bundle_text
)

# Auto-create all SQLite database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="KarmSetu API",
    description="NPU-Driven Wage Protection & Dignity Marketplace Production Backend",
    version="2.0.0"
)

# 1. Full CORS Middleware for physical mobile devices over Wi-Fi
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
        "service": "KarmSetu (MeraKaam AI v2.0) Production Engine",
        "version": "2.0.0",
        "database": "SQLite (Live Permanent Ledger)",
        "cors": "Enabled for all origins"
    }


# ============================================================================
# 1. LIVE ROUTE: /lock-contract (Ollama / Llama 3.2 NLP + SHA-256 SQLite Lock)
# ============================================================================
@app.post(
    "/lock-contract",
    response_model=schemas.LockContractResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Core Operations"]
)
def lock_contract(
    request: schemas.LockContractRequest,
    db: Session = Depends(get_db)
):
    """
    Accepts real spoken agreement text, invokes local Ollama (Llama 3.2:1b) engine,
    extracts structured work parameters, computes a true SHA-256 hash, and saves permanently to SQLite.
    """
    spoken_text = request.spoken_text.strip()
    if not spoken_text:
        raise HTTPException(status_code=400, detail="spoken_text cannot be empty.")

    # Call local Ollama Llama 3.2 instance
    ollama_url = "http://127.0.0.1:11434/api/generate"
    prompt = f"""You are the AI Contract Parser for KarmSetu. Extract the structured contract details from this spoken agreement between a contractor and a worker.
CRITICAL RULE: "worker_name" MUST be the actual worker being hired (e.g. Ramesh Arjun Kumar), NOT the employer/contractor.

Spoken Agreement: "{spoken_text}"

Respond strictly with a JSON object:
{{
  "worker_name": "Ramesh Arjun Kumar",
  "daily_wage_rate": 850.0,
  "duration_days": 30,
  "trade": "Master Mason",
  "site_location": "Metro Line 4 Pier Site in Mumbai",
  "site_latitude": 19.076000,
  "site_longitude": 72.877700
}}"""

    req_payload = json.dumps({
        "model": "llama3.2:1b",
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }).encode("utf-8")

    structured_data = {}
    try:
        req = urllib.request.Request(
            ollama_url,
            data=req_payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=45) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            raw_response = res_json.get("response", "{}")
            # Extract JSON cleanly with regex
            json_match = re.search(r"\{[\s\S]*\}", raw_response)
            if json_match:
                structured_data = json.loads(json_match.group(0))
            else:
                structured_data = json.loads(raw_response)
    except urllib.error.URLError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Local Ollama engine unreachable on http://localhost:11434 ({e}). Ensure 'ollama run llama3.2:1b' is active."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process spoken transcript via Llama 3.2: {str(e)}"
        )

    # Validate and normalize extracted parameters
    worker_name = structured_data.get("worker_name", "").strip()
    if not worker_name or "Contractor" in worker_name:
        # Fallback extract from regex in spoken text if model conflated names
        name_match = re.search(r"(?:worker|hire)\s+([A-Za-z\s]+?)\s+(?:as|at|for)", spoken_text, re.IGNORECASE)
        worker_name = name_match.group(1).strip() if name_match else (worker_name or "Verified Worker")

    daily_wage = structured_data.get("daily_wage_rate") or structured_data.get("daily_rate") or 850.0
    try:
        daily_wage = float(daily_wage)
    except (ValueError, TypeError):
        daily_wage = 850.0

    duration = structured_data.get("duration_days") or structured_data.get("duration") or 30
    try:
        duration = int(duration)
    except (ValueError, TypeError):
        duration = 30

    trade = structured_data.get("trade") or "General Construction Worker"
    site_location = structured_data.get("site_location") or structured_data.get("site") or "Designated Worksite"

    site_lat = request.site_latitude or structured_data.get("site_latitude")
    site_lon = request.site_longitude or structured_data.get("site_longitude")

    if site_lat is not None:
        try:
            site_lat = float(site_lat)
        except (ValueError, TypeError):
            site_lat = None

    if site_lon is not None:
        try:
            site_lon = float(site_lon)
        except (ValueError, TypeError):
            site_lon = None

    # Compute real SHA-256 hash of canonical terms
    canonical_terms = f"{worker_name}:{daily_wage}:{duration}:{trade}:{site_location}"
    contract_hash = hashlib.sha256(canonical_terms.encode("utf-8")).hexdigest()

    # Determine or generate worker ID hash
    worker_id_hash = request.worker_id_hash
    if not worker_id_hash:
        existing_worker = db.query(models.Worker).filter(models.Worker.worker_name == worker_name).first()
        if existing_worker:
            worker_id_hash = existing_worker.id_hash
        else:
            worker_id_hash = hashlib.sha256(f"WORKER_{worker_name}_{daily_wage}".encode("utf-8")).hexdigest()
            # Register worker record in SQLite ledger
            new_worker = models.Worker(
                id_hash=worker_id_hash,
                worker_name=worker_name,
                date_of_birth=datetime(1994, 8, 15).date()
            )
            db.add(new_worker)
            db.commit()

    # Check if this exact contract hash already exists
    existing_contract = db.query(models.Contract).filter(models.Contract.contract_hash == contract_hash).first()
    if existing_contract:
        return schemas.LockContractResponse(
            status="EXISTING_LOCKED_CONTRACT",
            message="Contract terms already locked and verified in SQLite ledger.",
            contract_id=existing_contract.id,
            contract_hash=existing_contract.contract_hash,
            worker_name=existing_contract.worker_name,
            worker_id_hash=existing_contract.worker_id_hash,
            daily_wage_rate=existing_contract.daily_wage_rate,
            duration_days=existing_contract.duration_days,
            trade=existing_contract.trade,
            site_location=existing_contract.site_location,
            site_latitude=existing_contract.site_latitude,
            site_longitude=existing_contract.site_longitude,
            created_at=existing_contract.created_at
        )

    # Save permanently to SQLite database
    new_contract = models.Contract(
        worker_name=worker_name,
        worker_id_hash=worker_id_hash,
        daily_wage_rate=daily_wage,
        duration_days=duration,
        trade=trade,
        site_location=site_location,
        site_latitude=site_lat,
        site_longitude=site_lon,
        contract_hash=contract_hash
    )
    db.add(new_contract)
    db.commit()
    db.refresh(new_contract)

    return schemas.LockContractResponse(
        status="LOCKED_CONTRACT_COMMITTED",
        message="Verbal contract extracted via Llama 3.2 and permanently locked to SQLite ledger with SHA-256.",
        contract_id=new_contract.id,
        contract_hash=new_contract.contract_hash,
        worker_name=new_contract.worker_name,
        worker_id_hash=new_contract.worker_id_hash,
        daily_wage_rate=new_contract.daily_wage_rate,
        duration_days=new_contract.duration_days,
        trade=new_contract.trade,
        site_location=new_contract.site_location,
        site_latitude=new_contract.site_latitude,
        site_longitude=new_contract.site_longitude,
        created_at=new_contract.created_at
    )


# ============================================================================
# 2. LIVE ROUTE: /daily-checkin (GPS Geofence + Facial Liveness Verification)
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
# 3. LIVE ROUTE: /audit-payment (Automated Deficit Detection & Evidence File)
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
    4. Detects deficit = Expected Funds - Amount Paid.
    5. If deficit > 0: Triggers 'Wage Theft Alert' and compiles a downloadable text evidence bundle.
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
    expected_payment = round(verified_workdays * daily_rate, 2)
    
    # Resolve paid amount from either amount_paid or received_amount field
    paid_val = audit.amount_paid if audit.amount_paid is not None else audit.received_amount
    amount_paid = round(float(paid_val or 0.0), 2)
    deficit = round(max(0.0, expected_payment - amount_paid), 2)

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
    download_filename = None

    if wage_theft_alert:
        status_label = "WAGE_THEFT_ALERT"
        download_filename = f"wage_theft_evidence_{worker.worker_name.replace(' ', '_')}_{worker.id_hash[:8]}.txt"
        download_url = f"/audit-payment/download-evidence?worker_id_hash={worker.id_hash}&amount_paid={amount_paid}&contract_id={contract.id}"
        message = (
            f"🚨 WAGE THEFT ALERT: Financial deficit of INR {deficit:,.2f} detected! "
            f"Expected INR {expected_payment:,.2f} for {verified_workdays} verified workdays (@ INR {daily_rate:,.2f}/day), "
            f"but received only INR {amount_paid:,.2f}."
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
            expected_amount=expected_payment,
            received_amount=amount_paid,
            deficit=deficit,
            attendance_records=attendance_logs
        )
    else:
        status_label = "VERIFIED_COMPLIANT"
        message = (
            f"Payment fully verified. Disbursed INR {amount_paid:,.2f} matches or exceeds "
            f"expected INR {expected_payment:,.2f} ({verified_workdays} workdays @ INR {daily_rate:,.2f}/day)."
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
        expected_payment=expected_payment,
        expected_amount=expected_payment,
        amount_paid=amount_paid,
        received_amount=amount_paid,
        deficit=deficit,
        message=message,
        download_file_name=download_filename,
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
    amount_paid: Optional[float] = Query(None, ge=0, description="Amount paid in INR"),
    received_amount: Optional[float] = Query(None, ge=0, description="Alternative amount paid parameter"),
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

    paid = amount_paid if amount_paid is not None else received_amount or 0.0
    verified_workdays = len(attendance_records)
    daily_rate = contract.daily_wage_rate
    expected_amount = round(verified_workdays * daily_rate, 2)
    deficit = round(max(0.0, expected_amount - paid), 2)

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
        received_amount=paid,
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
    # Bind to 0.0.0.0 so physical mobile phones on the same Wi-Fi network can connect directly
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
