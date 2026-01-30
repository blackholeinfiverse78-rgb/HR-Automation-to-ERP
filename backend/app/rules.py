import uuid
from datetime import datetime, timedelta
from .storage import get_events, save_alert, get_alerts, get_tenant_list
from .models import Alert

def check_stuck_candidates_for_tenant(tenant_id: str):
    events = get_events(tenant_id)
    alerts = get_alerts(tenant_id)
    
    # Reconstruct state
    candidate_state = {}
    for e in events:
        if e['entity_type'] == 'candidate':
            cid = e['entity_id']
            candidate_state[cid] = {
                'status': e['action'],
                'time': datetime.fromisoformat(e['timestamp'])
            }

    # SLA Rule: IF status == 'INTERVIEW_SCHEDULED' AND time > 7 days ago THEN Alert
    threshold = timedelta(days=7)
    now = datetime.utcnow()
    
    for cid, state in candidate_state.items():
        if state['status'] == 'INTERVIEW_SCHEDULED':
            time_in_stage = now - state['time']
            if time_in_stage > threshold:
                # Deduplication check
                already_alerted = any(
                    a['entity_id'] == cid and a['alert_type'] == 'SLA_BREACH_STUCK'
                    for a in alerts
                )
                
                if not already_alerted:
                    alert = Alert(
                        alert_id=str(uuid.uuid4()),
                        tenant_id=tenant_id,
                        alert_type="SLA_BREACH_STUCK",
                        severity="CRITICAL",
                        entity_id=cid,
                        reason=f"SLA Breach: Candidate stuck in INTERVIEW for {time_in_stage.days} days",
                        triggered_at=now,
                        metadata={
                            "days_in_stage": time_in_stage.days,
                            "threshold_days": 7
                        }
                    )
                    save_alert(alert)

def run_rules():
    print("Running Global Rule Evaluation across all tenants...")
    tenants = get_tenant_list()
    for tenant_id in tenants:
        print(f" - Processing Tenant: {tenant_id}")
        check_stuck_candidates_for_tenant(tenant_id)

