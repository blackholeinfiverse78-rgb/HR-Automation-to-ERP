# HR Automation to ERP - Event & Alert Engine (Hardened v2.0)

A high-reliability, deterministic HR automation system that turns recruiter actions into ERP-grade events, alerts, and signals.

---

## 🛡️ System Hardening & Trust (v2.0)
This version has been hardened for enterprise trust:
- **Mandatory Multi-Tenancy**: `tenant_id` is required for every event and signal. Data is physically isolated.
- **Frozen Contracts**: Explicit schemas for all events (`HR_EVENT_SHORTLISTED`, `HR_ALERT_STUCK`, etc).
- **Idempotency Guarantees**: `EMPLOYEE_CREATED` signals are restart-safe and will never duplicate even if the sync pipeline is rerun.
- **Traceable Invariants**: Alerts are derived from real system state (SLAs) with full trace proofs.

---

## 📚 Documentation
- [System Capabilities & Boundaries](./docs/SYSTEM_CAPABILITIES.md)
- [Event & Signal Contracts](./docs/contracts/schemas.md)

---

## 🏃 Running Locally

### 1. Prerequisites
- Python 3.12+ (Installed via winget)
- `pip`

### 2. Setup & Backend
```powershell
# Install dependencies
pip install -r requirements.txt

# Start the Backend (API)
uvicorn backend.app.main:app --reload --port 8000
```

### 3. Frontend Dashboard
```powershell
cd frontend
python -m http.server 8080
```
*Dashboard: [http://localhost:8080](http://localhost:8080)*

---

## 🧪 Verification
Run the system-grade test suite to verify isolation, idempotency, and contract compliance:
```powershell
python test_flow.py
```

---

## 📂 Project Structure
- `backend/app/`: FastAPI application code.
- `data/{tenant_id}/`: Isolated persistent JSON stores.
- `docs/`: System documentation and contracts.
- `frontend/`: Glassmorphic Dashboard UI.
- `test_flow.py`: High-reliability verification suite.

