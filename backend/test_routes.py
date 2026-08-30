import os
import sys
import hashlib
from datetime import date

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
from database import engine, Base

# Clean and recreate test database tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_full_operational_flow():
    print("--- 1. Testing Health Endpoint ---")
    res = client.get("/")
    assert res.status_code == 200
    print("Health check response:", res.json())

    print("\n--- 2. Registering Worker ---")
    worker_raw_id = "AADHAAR_SAMPLE_WORKER_001"
    worker_id_hash = hashlib.sha256(worker_raw_id.encode()).hexdigest()
    worker_payload = {
        "id_hash": worker_id_hash,
        "worker_name": "Ramesh Arjun Kumar",
        "date_of_birth": "1992-05-14"
    }
    res = client.post("/workers", json=worker_payload)
    assert res.status_code == 201
    print("Worker registered:", res.json())

    print("\n--- 3. Creating Locked Contract ---")
    contract_raw = "CONTRACT:Ramesh Arjun Kumar:850.00:30:Mason:Metro Line 4 Site Mumbai"
    contract_hash = hashlib.sha256(contract_raw.encode()).hexdigest()
    contract_payload = {
        "worker_name": "Ramesh Arjun Kumar",
        "worker_id_hash": worker_id_hash,
        "daily_wage_rate": 850.0,
        "duration_days": 30,
        "trade": "Mason",
        "site_location": "Metro Line 4 Site Mumbai (19.076000, 72.877700)",
        "site_latitude": 19.076000,
        "site_longitude": 72.877700,
        "contract_hash": contract_hash
    }
    res = client.post("/contracts", json=contract_payload)
    assert res.status_code == 201
    contract_id = res.json()["id"]
    print("Contract created with ID:", contract_id)

    print("\n--- 4. Testing /daily-checkin Valid Proximity ---")
    checkin_payload = {
        "worker_id_hash": worker_id_hash,
        "latitude": 19.076050,  # ~6 meters away
        "longitude": 72.877720,
        "facial_liveness_pass": True
    }
    res = client.post("/daily-checkin", json=checkin_payload)
    assert res.status_code == 201
    print("Check-in 1 result:", res.json())

    print("\n--- 5. Testing /daily-checkin (2nd & 3rd Workdays) ---")
    # Log 2 more workdays
    for i in range(2, 4):
        res = client.post("/daily-checkin", json=checkin_payload)
        assert res.status_code == 201
        print(f"Check-in {i} success. Attendance ID: {res.json()['attendance_id']}")

    print("\n--- 6. Testing /daily-checkin Error Handling ---")
    # A) Far away location (Geofence violation)
    bad_location = {
        "worker_id_hash": worker_id_hash,
        "latitude": 28.6139,  # New Delhi (~1150 km away)
        "longitude": 77.2090,
        "facial_liveness_pass": True
    }
    res_bad_loc = client.post("/daily-checkin", json=bad_location)
    assert res_bad_loc.status_code == 400
    print("Geofence violation handled gracefully:", res_bad_loc.json()["detail"])

    # B) Facial liveness fail
    bad_liveness = {
        "worker_id_hash": worker_id_hash,
        "latitude": 19.076000,
        "longitude": 72.877700,
        "facial_liveness_pass": False
    }
    res_bad_live = client.post("/daily-checkin", json=bad_liveness)
    assert res_bad_live.status_code == 400
    print("Liveness failure handled gracefully:", res_bad_live.json()["detail"])

    # C) Missing / non-existent worker
    bad_worker = {
        "worker_id_hash": "0000000000000000000000000000000000000000000000000000000000000000",
        "latitude": 19.076000,
        "longitude": 72.877700,
        "facial_liveness_pass": True
    }
    res_bad_worker = client.post("/daily-checkin", json=bad_worker)
    assert res_bad_worker.status_code == 404
    print("Non-existent worker handled gracefully:", res_bad_worker.json()["detail"])

    print("\n--- 7. Testing /audit-payment (Fully Paid Case) ---")
    # 3 verified days * 850 = 2550
    audit_ok = {
        "worker_id_hash": worker_id_hash,
        "received_amount": 2550.0
    }
    res_audit_ok = client.post("/audit-payment", json=audit_ok)
    assert res_audit_ok.status_code == 200
    print("Audit compliant case:", res_audit_ok.json()["status"], "-", res_audit_ok.json()["message"])

    print("\n--- 8. Testing /audit-payment (Wage Theft Alert Case) ---")
    # Paid only 1000 instead of 2550 (Deficit = 1550)
    audit_theft = {
        "worker_id_hash": worker_id_hash,
        "received_amount": 1000.0
    }
    res_audit_theft = client.post("/audit-payment", json=audit_theft)
    assert res_audit_theft.status_code == 200
    theft_data = res_audit_theft.json()
    assert theft_data["wage_theft_alert"] is True
    assert theft_data["status"] == "WAGE_THEFT_ALERT"
    assert theft_data["deficit"] == 1550.0
    print("Wage theft alert status:", theft_data["status"])
    print("Underpayment Deficit:", theft_data["deficit"])
    print("Download Evidence URL:", theft_data["download_evidence_url"])
    print("\nEvidence Bundle Preview:\n")
    print(theft_data["evidence_bundle"])

    print("\n--- 9. Testing Download Evidence Endpoint ---")
    dl_url = theft_data["download_evidence_url"]
    res_dl = client.get(dl_url)
    assert res_dl.status_code == 200
    assert "Content-Disposition" in res_dl.headers
    assert "KARMSETU WAGE THEFT AUDIT & EVIDENCE BUNDLE" in res_dl.text
    print("Evidence file download verified successfully! Content length:", len(res_dl.text), "bytes")

    print("\n>>> ALL OPERATIONAL ROUTE TESTS PASSED SUCCESSFULLY! <<<")


if __name__ == "__main__":
    test_full_operational_flow()
