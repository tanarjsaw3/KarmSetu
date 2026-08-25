import sys
import os
import re
import json
import hashlib
import warnings
from datetime import datetime, timezone

# Suppress Starlette/TestClient deprecation warnings for clean test logs
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Ensure UTF-8 output encoding in Windows environment
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from fastapi.testclient import TestClient
from database import engine, Base
import models
from main import app

# Reset SQLite test database for a clean simulation run
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def run_pipeline_simulation():
    print("=" * 80)
    print("       KARMSETU (MeraKaam AI v2.0) END-TO-END PIPELINE SIMULATION")
    print("=" * 80)

    # ------------------------------------------------------------------------
    # STAGE 1 & 2: Call Live /lock-contract endpoint (Ollama Llama 3.2 + SHA-256 Lock)
    # ------------------------------------------------------------------------
    spoken_text = (
        "I, Contractor Verma, agree to hire worker Ramesh Arjun Kumar as a Master Mason "
        "at a daily wage rate of 850 INR for a duration of 30 days at the Metro Line 4 "
        "Pier Site in Mumbai at coordinates 19.076000, 72.877700 with weekly disbursements."
    )
    print(f"\n[Stage 1 & 2] 🎙️ Calling Live /lock-contract with Spoken Agreement:\n  \"{spoken_text}\"")

    lock_payload = {
        "spoken_text": spoken_text,
        "site_latitude": 19.076000,
        "site_longitude": 72.877700
    }
    lock_resp = client.post("/lock-contract", json=lock_payload)
    assert lock_resp.status_code == 201, f"Lock contract failed: {lock_resp.text}"
    contract_data = lock_resp.json()

    print("\n-> /lock-contract Output:")
    print(f"   Status          : {contract_data['status']}")
    print(f"   Contract ID     : #{contract_data['contract_id']}")
    print(f"   Worker Name     : {contract_data['worker_name']}")
    print(f"   Worker ID Hash  : {contract_data['worker_id_hash']}")
    print(f"   Daily Rate      : INR {contract_data['daily_wage_rate']:,.2f} / day")
    print(f"   Duration        : {contract_data['duration_days']} days")
    print(f"   Trade           : {contract_data['trade']}")
    print(f"   Site Location   : {contract_data['site_location']}")
    print(f"   Locked SHA-256  : {contract_data['contract_hash']}")

    contract_id = contract_data["contract_id"]
    worker_id_hash = contract_data["worker_id_hash"]
    contract_hash = contract_data["contract_hash"]

    # ------------------------------------------------------------------------
    # STAGE 3: Register 3 Days of Verified Daily Check-Ins (GPS + Liveness)
    # ------------------------------------------------------------------------
    print("\n[Stage 3] 📍 Registering 3 Days of Geofence + Biometric Daily Check-Ins...")
    checkin_coordinates = [
        (19.076010, 72.877712, "Day 1 (Morning Check-In)"),
        (19.076018, 72.877705, "Day 2 (Morning Check-In)"),
        (19.075995, 72.877698, "Day 3 (Morning Check-In)")
    ]

    for lat, lon, label in checkin_coordinates:
        checkin_payload = {
            "worker_id_hash": worker_id_hash,
            "latitude": lat,
            "longitude": lon,
            "facial_liveness_pass": True,
            "contract_id": contract_id
        }
        res = client.post("/daily-checkin", json=checkin_payload)
        assert res.status_code == 201, f"Check-in failed: {res.text}"
        data = res.json()
        print(f"-> {label}: Verified! Attendance ID #{data['attendance_id']} | GPS: {data['gps_coordinates']} | Distance: {data['distance_meters']}m | Status: {data['status']}")

    # ------------------------------------------------------------------------
    # STAGE 4: Run Live /audit-payment with amount_paid Deficit
    # ------------------------------------------------------------------------
    print("\n[Stage 4] 🚨 Calling Live /audit-payment with Deficit (INR 1,000 paid vs INR 2,550 expected)...")
    # Expected wages for 3 days @ 850 INR = 2,550 INR
    # Actual disbursed payment = 1,000 INR (Deficit = 1,550 INR)
    amount_paid = 1000.0
    audit_payload = {
        "worker_id_hash": worker_id_hash,
        "amount_paid": amount_paid,
        "contract_id": contract_id
    }
    audit_resp = client.post("/audit-payment", json=audit_payload)
    assert audit_resp.status_code == 200, f"Audit failed: {audit_resp.text}"
    audit_data = audit_resp.json()

    print(f"-> Audit Status               : {audit_data['status']}")
    print(f"-> Wage Theft Alert Triggered : {audit_data['wage_theft_alert']}")
    print(f"-> Verified Workdays Logged   : {audit_data['verified_workdays']}")
    print(f"-> Total Expected Payment     : INR {audit_data['expected_payment']:,.2f}")
    print(f"-> Actual Amount Paid         : INR {audit_data['amount_paid']:,.2f}")
    print(f"-> Underpayment Deficit       : INR {audit_data['deficit']:,.2f}")
    print(f"-> Download File Name         : {audit_data['download_file_name']}")
    print(f"-> Download Evidence URL      : {audit_data['download_evidence_url']}")

    assert audit_data["wage_theft_alert"] is True, "Wage theft alert was not triggered!"
    assert audit_data["deficit"] == 1550.0, f"Deficit calculation error: expected 1550.0, got {audit_data['deficit']}"
    assert audit_data["download_evidence_url"] is not None, "Download evidence URL missing!"

    # ------------------------------------------------------------------------
    # STAGE 5: Verify Active Downloadable Evidence Bundle (.txt)
    # ------------------------------------------------------------------------
    print("\n[Stage 5] 📄 Downloading & Validating Legal Evidence Bundle File...")
    dl_url = audit_data["download_evidence_url"]
    dl_resp = client.get(dl_url)
    assert dl_resp.status_code == 200, f"Failed to download evidence bundle: {dl_resp.text}"
    evidence_content = dl_resp.text

    assert "KARMSETU WAGE THEFT AUDIT & EVIDENCE BUNDLE" in evidence_content
    assert worker_id_hash in evidence_content
    assert contract_hash in evidence_content
    assert "INR 1,550.00" in evidence_content

    print("-> Evidence Bundle Downloaded Successfully!")
    print(f"-> Content Size: {len(evidence_content)} bytes")
    print("\n--- Evidence Bundle Summary Snapshot ---")
    print("\n".join(evidence_content.splitlines()[:25]))
    print("...")

    print("\n" + "=" * 80)
    print(">>> FULL PRODUCTION PIPELINE SIMULATION PASSED 100% SUCCESSFULLY! <<<")
    print("KarmSetu (MeraKaam AI v2.0) Live Endpoints are fully operational.")
    print("=" * 80)


if __name__ == "__main__":
    run_pipeline_simulation()
