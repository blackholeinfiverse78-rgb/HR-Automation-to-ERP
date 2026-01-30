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

    # Rule 1: INTERVIEW_SCHEDULED SLA
    interview_threshold = timedelta(days=7)
    # Rule 2: SHORTLISTED SLA (New Invariant)
    shortlist_threshold = timedelta(days=3)
    
    now = datetime.utcnow()
    
    for cid, state in candidate_state.items():
        time_in_stage = now - state['time']
        alert_type = "SLA_BREACH_STUCK"
        
        if state['status'] == 'INTERVIEW_SCHEDULED' and time_in_stage > interview_threshold:
            reason = f"SLA Breach: Candidate stuck in INTERVIEW for {time_in_stage.days} days"
            trigger_alert(tenant_id, cid, reason, time_in_stage.days, 7, alerts)
            
        elif state['status'] == 'SHORTLISTED' and time_in_stage > shortlist_threshold:
            reason = f"SLA Breach: Candidate shortlisted but no action for {time_in_stage.days} days"
            trigger_alert(tenant_id, cid, reason, time_in_stage.days, 3, alerts)

def trigger_alert(tenant_id, entity_id, reason, days, threshold, existing_alerts):
    # Deduplication check
    already_alerted = any(
        a['entity_id'] == entity_id and a['reason'] == reason
        for a in existing_alerts
    )
    
    if not already_alerted:
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            alert_type="SLA_BREACH_STUCK",
            severity="CRITICAL",
            entity_id=entity_id,
            reason=reason,
            triggered_at=datetime.utcnow(),
            metadata={
                "days_in_stage": days,
                "threshold_days": threshold
            }
        )
        save_alert(alert)

def run_rules():
    print("Running Global Rule Evaluation across all tenants...")
    tenants = get_tenant_list()
    for tenant_id in tenants:
        print(f" - Processing Tenant: {tenant_id}")
        check_stuck_candidates_for_tenant(tenant_id)


