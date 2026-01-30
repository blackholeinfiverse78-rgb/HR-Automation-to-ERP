import json
import os
from datetime import datetime
from .models import HREvent, Alert, ERPSignal

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
EVENTS_FILE = os.path.join(DATA_DIR, "events.json")
ALERTS_FILE = os.path.join(DATA_DIR, "alerts.json")
ERP_FILE = os.path.join(DATA_DIR, "erp_signals.json")

def _get_tenant_dir(tenant_id: str):
    t_dir = os.path.join(DATA_DIR, tenant_id)
    os.makedirs(t_dir, exist_ok=True)
    return t_dir

def _get_tenant_file(tenant_id: str, filename: str):
    return os.path.join(_get_tenant_dir(tenant_id), filename)

def _ensure_file(filepath):
    if not os.path.exists(filepath):
        with open(filepath, "w") as f:
            json.dump([], f)

def _append_to_file(filepath, data: dict, idempotency_key: str = None):
    _ensure_file(filepath)
    with open(filepath, "r") as f:
        try:
            content = json.load(f)
        except json.JSONDecodeError:
            content = []
    
    # Idempotency check
    if idempotency_key:
        if any(item.get('idempotency_key') == idempotency_key for item in content):
            print(f"[STORAGE] Duplicate signal detected: {idempotency_key}. Skipping.")
            return False

    content.append(data)
    with open(filepath, "w") as f:
        json.dump(content, f, indent=2, default=str)
    return True

def save_hr_event(event: HREvent):
    filepath = _get_tenant_file(event.tenant_id, "events.json")
    print(f"[EVENT SAVED] Tenant: {event.tenant_id} | {event.action} on {event.entity_id}")
    return _append_to_file(filepath, event.dict(), event.idempotency_key)

def save_alert(alert: Alert):
    filepath = _get_tenant_file(alert.tenant_id, "alerts.json")
    print(f"[ALERT RAISED] Tenant: {alert.tenant_id} | {alert.alert_type}: {alert.reason}")
    _append_to_file(filepath, alert.dict())

def save_erp_signal(signal: ERPSignal):
    filepath = _get_tenant_file(signal.tenant_id, "erp_signals.json")
    print(f"[ERP SIGNAL] Tenant: {signal.tenant_id} | {signal.event_type} for {signal.entity_id}")
    _append_to_file(filepath, signal.dict())

def get_tenant_list():
    if not os.path.exists(DATA_DIR):
        return []
    return [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]

def get_events(tenant_id: str):
    filepath = _get_tenant_file(tenant_id, "events.json")
    _ensure_file(filepath)
    with open(filepath, "r") as f:
        return json.load(f)

def get_alerts(tenant_id: str):
    filepath = _get_tenant_file(tenant_id, "alerts.json")
    _ensure_file(filepath)
    with open(filepath, "r") as f:
        return json.load(f)

def get_erp_signals(tenant_id: str):
    filepath = _get_tenant_file(tenant_id, "erp_signals.json")
    _ensure_file(filepath)
    with open(filepath, "r") as f:
        return json.load(f)

