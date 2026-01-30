import uuid
from .models import HREvent, ERPSignal
from .storage import save_erp_signal, get_erp_signals, get_tenant_list, get_events
from datetime import datetime

def map_event_to_erp(event: HREvent):
    """
    Translates HR Domain Events to ERP Signals using the EMS/Artha Contract v2.0.
    """
    signals = []
    
    # RULE 1: CANDIDATE.HIRED -> EMPLOYEE_CREATED
    if event.action == "HIRED" and event.entity_type == "candidate":
        emp_id = event.entity_id.replace("cand_", "emp_")
        
        signal = ERPSignal(
            signal_id=str(uuid.uuid4()),
            contract_version="2.0",
            tenant_id=event.tenant_id,
            event_type="EMPLOYEE_CREATED",
            entity_id=emp_id,
            effective_date=datetime.utcnow().date().isoformat(),
            payload={
                "hr_reference_id": event.entity_id,
                "hiring_manager_id": event.actor_id,
                "onboarding_status": "PENDING",
                "data_integrity_check": "VALIDATED"
            },
            audit_trail={
                "original_event_id": event.event_id,
                "original_timestamp": event.timestamp.isoformat(),
                "trace_context": f"HR_FLOW_{event.tenant_id}_{event.entity_id}"
            }
        )
        signals.append(signal)

    return signals

def process_erp_sync():
    """
    Processes all tenants to generate versioned ERP signals.
    """
    tenants = get_tenant_list()
    for tenant_id in tenants:
        print(f" - Syncing ERP for Tenant: {tenant_id}")
        events = get_events(tenant_id)
        existing_signals = get_erp_signals(tenant_id)
        
        # Deduplication based on audit trail (original event reference)
        processed_event_ids = set()
        for s in existing_signals:
            if 'audit_trail' in s and 'original_event_id' in s['audit_trail']:
                processed_event_ids.add(s['audit_trail']['original_event_id'])
        
        count = 0
        for e_dict in events:
            e = HREvent(**e_dict)
            if e.event_id in processed_event_ids:
                continue
                
            generated_signals = map_event_to_erp(e)
            for sig in generated_signals:
                save_erp_signal(sig)
                count += 1
        
        if count > 0:
            print(f"   Done. New Signals: {count}")

