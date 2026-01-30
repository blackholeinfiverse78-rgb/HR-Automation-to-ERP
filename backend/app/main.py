import uuid
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from .models import HREvent
from .storage import save_hr_event, get_events, get_alerts, get_erp_signals, get_tenant_list
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="HR Automation Event & ERP Bridge (v2)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Simulation Models ---
class ShortlistRequest(BaseModel):
    candidate_id: str
    recruiter_id: str
    tenant_id: str
    idempotency_key: str = None

class InterviewScheduleRequest(BaseModel):
    candidate_id: str
    recruiter_id: str
    time_slot: datetime
    tenant_id: str
    idempotency_key: str = None

# --- Core Event Logic ---
def emit_hr_event(tenant_id: str, entity_type: str, entity_id: str, action: str, actor_id: str, actor_role: str, payload: dict = None, idempotency_key: str = None):
    event = HREvent(
        event_id=str(uuid.uuid4()),
        idempotency_key=idempotency_key or str(uuid.uuid4()),
        tenant_id=tenant_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        actor_id=actor_id,
        actor_role=actor_role,
        timestamp=datetime.utcnow(),
        payload=payload or {}
    )
    save_hr_event(event)
    return event

# --- Intercepted Actions ---

@app.post("/actions/shortlist")
def recruiter_shortlist_candidate(req: ShortlistRequest):
    event = emit_hr_event(
        tenant_id=req.tenant_id,
        entity_type="candidate",
        entity_id=req.candidate_id,
        action="SHORTLISTED",
        actor_id=req.recruiter_id,
        actor_role="RECRUITER",
        idempotency_key=req.idempotency_key
    )
    return {"status": "success", "event_id": event.event_id}

@app.post("/actions/interview")
def recruiter_schedule_interview(req: InterviewScheduleRequest):
    event = emit_hr_event(
        tenant_id=req.tenant_id,
        entity_type="candidate",
        entity_id=req.candidate_id,
        action="INTERVIEW_SCHEDULED",
        actor_id=req.recruiter_id,
        actor_role="RECRUITER",
        payload={"scheduled_time": str(req.time_slot)},
        idempotency_key=req.idempotency_key
    )
    return {"status": "success", "event_id": event.event_id}

@app.post("/actions/hire")
def recruiter_hire_candidate(req: ShortlistRequest): 
    event = emit_hr_event(
        tenant_id=req.tenant_id,
        entity_type="candidate",
        entity_id=req.candidate_id,
        action="HIRED",
        actor_id=req.recruiter_id,
        actor_role="RECRUITER",
        idempotency_key=req.idempotency_key
    )
    return {"status": "success", "event_id": event.event_id}

@app.post("/actions/debug/stuck-candidate")
def debug_create_stuck_candidate(req: ShortlistRequest):
    from datetime import timedelta
    # 4 days ago (triggers the 3-day Shortlist SLA)
    old_time = datetime.utcnow() - timedelta(days=4)
    
    event = HREvent(
        event_id=str(uuid.uuid4()),
        idempotency_key=str(uuid.uuid4()),
        tenant_id=req.tenant_id,
        entity_type="candidate",
        entity_id=req.candidate_id,
        action="SHORTLISTED",
        actor_id="SYSTEM_DEBUG",
        actor_role="DEBUG_SYSTEM",
        timestamp=old_time
    )
    save_hr_event(event) 
    return {"status": "injected_old_shortlisted_event", "timestamp": str(old_time)}


# --- Read-Only Endpoints ---

@app.get("/tenants")
def list_tenants():
    return get_tenant_list()

@app.get("/events")
def read_events(tenant_id: str = Query(...)):
    return get_events(tenant_id)

@app.get("/alerts")
def read_alerts(tenant_id: str = Query(...)):
    return get_alerts(tenant_id)

@app.get("/erp-signals")
def read_erp_signals(tenant_id: str = Query(...)):
    return get_erp_signals(tenant_id)

@app.get("/")
def root():
    return {"message": "HR Automation System v2 (Multi-tenant) Operational"}

@app.post("/system/process")
def trigger_system_processing():
    from .rules import run_rules
    from .erp_mapper import process_erp_sync
    run_rules()
    process_erp_sync()
    return {"status": "Processing Complete", "timestamp": datetime.utcnow()}

@app.get("/explain/{entity_id}")
def explain_action(entity_id: str, tenant_id: str = Query(...)):
    alerts = get_alerts(tenant_id)
    events = get_events(tenant_id)
    
    entity_alerts = [a for a in alerts if a['entity_id'] == entity_id]
    entity_events = [e for e in events if e['entity_id'] == entity_id]
    
    if not entity_alerts and not entity_events:
        return {"explanation": "No history found for this entity in this tenant."}
    
    summary = f"History for {entity_id} (Tenant: {tenant_id}): "
    if entity_alerts:
        summary += f"Target flagged with {len(entity_alerts)} alerts. Latest: {entity_alerts[-1]['reason']}. "
    
    if entity_events:
        summary += f"Last action recorded: {entity_events[-1]['action']} by {entity_events[-1].get('actor_role', 'unknown')}."

    return {
        "entity_id": entity_id,
        "tenant_id": tenant_id,
        "explanation": summary,
        "raw_events_count": len(entity_events),
        "raw_alerts_count": len(entity_alerts)
    }

