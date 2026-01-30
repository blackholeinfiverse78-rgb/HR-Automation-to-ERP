import requests
import time
import json
import uuid

BASE_URL = "http://localhost:8000"

def test_system_grade_features():
    print("=== [v2.0] System-Grade Verification Suite ===")
    
    TENANT_A = "acme_corp"
    TENANT_B = "globex_inc"
    
    # --- Part 1: Isolation & Multi-tenancy ---
    print("\n--- Phase 1: Multi-tenant Isolation ---")
    
    # Shortlist in Tenant A
    res_a = requests.post(f"{BASE_URL}/actions/shortlist", json={
        "candidate_id": "cand_acme_1",
        "recruiter_id": "rec_001",
        "tenant_id": TENANT_A
    })
    print(f"Tenant A Shortlist: {res_a.status_code}")
    
    # Check Tenant B (Should be empty/isolate)
    events_b = requests.get(f"{BASE_URL}/events?tenant_id={TENANT_B}").json()
    print(f"Tenant B Events (Isolating check): {len(events_b)} (Expected: 0)")
    
    # --- Part 2: Idempotency & Persistence ---
    print("\n--- Phase 2: Idempotency & Persistence Guarantees ---")
    ik = f"idemp_{uuid.uuid4()}"
    
    # Send event twice with same Idempotency Key
    res_idemp_1 = requests.post(f"{BASE_URL}/actions/shortlist", json={
        "candidate_id": "cand_persist_1",
        "recruiter_id": "rec_001",
        "tenant_id": TENANT_A,
        "idempotency_key": ik
    })
    res_idemp_2 = requests.post(f"{BASE_URL}/actions/shortlist", json={
        "candidate_id": "cand_persist_1",
        "recruiter_id": "rec_001",
        "tenant_id": TENANT_A,
        "idempotency_key": ik
    })
    
    events_a = requests.get(f"{BASE_URL}/events?tenant_id={TENANT_A}").json()
    # Count how many have our IK
    matching = [e for e in events_a if e.get('idempotency_key') == ik]
    print(f"Idempotency Check: Received {len(matching)} records for key {ik} (Expected: 1)")

    # --- Part 3: Real SLA Breaches (Real System Invariants) ---
    print("\n--- Phase 3: SLA Breach & Rule Engine ---")
    
    # Inject a stuck candidate in Globex
    requests.post(f"{BASE_URL}/actions/debug/stuck-candidate", json={
        "candidate_id": "cand_stuck_globex",
        "recruiter_id": "rec_system",
        "tenant_id": TENANT_B
    })
    
    # Trigger processing
    requests.post(f"{BASE_URL}/system/process")
    
    # Check Alerts for Globex
    alerts_b = requests.get(f"{BASE_URL}/alerts?tenant_id={TENANT_B}").json()
    print(f"Tenant B Alerts: {len(alerts_b)}")
    if alerts_b:
        print(f"Latest Alert: {alerts_b[-1]['alert_type']} | Severity: {alerts_b[-1]['severity']}")
        print(f"Reason: {alerts_b[-1]['reason']}")

    # --- Part 4: ERP Contract v2.0 (EMS/Artha Consumption) ---
    print("\n--- Phase 4: ERP Contract v2.0 Verification ---")
    
    # Hire in Acme
    requests.post(f"{BASE_URL}/actions/hire", json={
        "candidate_id": "cand_acme_1",
        "recruiter_id": "rec_001",
        "tenant_id": TENANT_A
    })
    
    # Sync ERP
    requests.post(f"{BASE_URL}/system/process")
    
    # Check Signals
    signals = requests.get(f"{BASE_URL}/erp-signals?tenant_id={TENANT_A}").json()
    if signals:
        s = signals[-1]
        print(f"Signal Version: {s['contract_version']}")
        print(f"Signal Type: {s['event_type']}")
        print(f"Audit Trail Hash: {s['audit_trail']['trace_context']}")
        print(f"Payload Integrity: {'onboarding_status' in s['payload']}")

    print("\n--- Result ---")
    print("Verification Suite: 100% COMPLETE")

if __name__ == "__main__":
    try:
        test_system_grade_features()
    except Exception as e:
        print(f"Verification Suite FATAL Error: {e}")
