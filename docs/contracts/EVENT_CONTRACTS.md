# Event Contracts (v2.0)

This document defines the formal contracts for events, alerts, and signals within the HR-to-ERP Automation Bridge.

## 1. HR_EVENT_SHORTLISTED
**Producer:** Recruitment Dashboard / ATS  
**Description:** Emitted when a candidate is shortlisted for a position.

### Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "tenant_id": { "type": "string", "description": "Mandatory Tenant ID" },
    "idempotency_key": { "type": "string" },
    "entity_type": { "type": "string", "const": "candidate" },
    "entity_id": { "type": "string" },
    "action": { "type": "string", "const": "SHORTLISTED" },
    "actor_id": { "type": "string" },
    "actor_role": { "type": "string" },
    "timestamp": { "type": "string", "format": "date-time" },
    "payload": { "type": "object" }
  },
  "required": ["event_id", "tenant_id", "idempotency_key", "entity_type", "entity_id", "action", "timestamp"]
}
```

---

## 2. HR_ALERT_STUCK
**Producer:** SLA Rule Engine  
**Description:** Emitted when a candidate state remains unchanged beyond a defined threshold.

### Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "alert_id": { "type": "string", "format": "uuid" },
    "tenant_id": { "type": "string", "description": "Mandatory Tenant ID" },
    "alert_type": { "type": "string", "const": "SLA_BREACH_STUCK" },
    "severity": { "type": "string", "enum": ["INFO", "WARN", "CRITICAL"] },
    "entity_id": { "type": "string" },
    "reason": { "type": "string" },
    "triggered_at": { "type": "string", "format": "date-time" },
    "metadata": { 
      "type": "object",
      "properties": {
        "days_in_stage": { "type": "integer" },
        "threshold_days": { "type": "integer" }
      }
    }
  },
  "required": ["alert_id", "tenant_id", "alert_type", "severity", "entity_id", "reason", "triggered_at"]
}
```

---

## 3. ERP_EVENT_EMPLOYEE_CREATED
**Producer:** ERP Mapper  
**Description:** The final signal sent to the ERP system when a candidate is hired.

### Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "signal_id": { "type": "string", "format": "uuid" },
    "contract_version": { "type": "string", "const": "2.0" },
    "tenant_id": { "type": "string", "description": "Mandatory Tenant ID" },
    "event_type": { "type": "string", "const": "EMPLOYEE_CREATED" },
    "entity_id": { "type": "string", "description": "ERP Employee ID" },
    "effective_date": { "type": "string", "format": "date" },
    "payload": {
      "type": "object",
      "properties": {
        "hr_reference_id": { "type": "string" },
        "onboarding_status": { "type": "string" }
      }
    },
    "audit_trail": {
      "type": "object",
      "properties": {
        "original_event_id": { "type": "string" },
        "trace_context": { "type": "string" }
      }
    }
  },
  "required": ["signal_id", "contract_version", "tenant_id", "event_type", "entity_id", "payload", "audit_trail"]
}
```

---

## System Emission vs. ERP Consumption

- **Our System Emits:** Highly granular HR events and internal SLA alerts. 
- **ERP Consumes:** Refined, idempotent signals that map directly to HR records (e.g., creating an employee profile).
- **Bridge Role:** The Automation Bridge acts as a "Trust Layer," ensuring that only valid, non-duplicate, and tenant-isolated data reaches the ERP via explicit mapping rules.
