from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

class HREvent(BaseModel):
    """
    Contract: HR_EVENT (v2.0)
    Mandatory: tenant_id, event_id
    """
    event_id: str = Field(..., description="Unique ID for this event (UUID/ULID)")
    tenant_id: str = Field(..., description="Mandatory Target Tenant ID for isolation")
    idempotency_key: str = Field(..., description="Key to prevent duplicate processing")
    entity_type: str = Field(..., description="e.g., candidate, employee")
    entity_id: str
    action: str = Field(..., description="e.g., SHORTLISTED, HIRED")
    actor_id: str = Field(..., description="ID of the person/system acting")
    actor_role: str = Field(..., description="e.g., RECRUITER, SYSTEM")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: Optional[dict] = Field(default={}, description="Domain-specific details")

class Alert(BaseModel):
    """
    Contract: HR_ALERT (v2.0)
    Mandatory: tenant_id, alert_id
    """
    alert_id: str = Field(..., description="Unique Alert ID")
    tenant_id: str = Field(..., description="Mandatory Tenant ID")
    alert_type: str = Field(..., description="e.g. SLA_BREACH_STUCK")
    severity: Literal["INFO", "WARN", "CRITICAL"]
    entity_id: str
    reason: str
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = Field(default={}, description="Evidence for the alert")

class ERPSignal(BaseModel):
    """
    Contract: ERP_SIGNAL (v2.0)
    Mandatory: tenant_id, signal_id
    """
    signal_id: str
    contract_version: str = "2.0"
    tenant_id: str = Field(..., description="Mandatory Tenant ID")
    event_type: Literal["EMPLOYEE_CREATED", "ONBOARDING_INITIATED", "SLA_VIOLATION_REPORT"]
    entity_id: str 
    effective_date: str
    payload: dict = Field(..., description="Contract-validated payload")
    audit_trail: dict = Field(default_factory=dict, description="Original HR Event references")


