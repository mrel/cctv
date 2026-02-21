"""Alert schemas for API requests and responses."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AlertConditions(BaseModel):
    """Alert conditions schema."""
    subject_types: Optional[List[str]] = None
    subject_ids: Optional[List[UUID]] = None
    cameras: Optional[List[UUID]] = None
    camera_zones: Optional[List[Dict[str, Any]]] = None
    min_confidence: Optional[float] = Field(None, ge=0, le=1)
    time_range: Optional[Dict[str, str]] = None
    days: Optional[List[str]] = None
    exclude_types: Optional[List[str]] = None


class AlertActions(BaseModel):
    """Alert actions schema."""
    webhook: Optional[str] = None
    email: Optional[List[str]] = None
    sms: Optional[List[str]] = None
    push: Optional[bool] = False


class AlertRuleBase(BaseModel):
    """Base alert rule schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    rule_type: str = Field(..., pattern="^(blacklist|whitelist|geofence|loitering|tailgating|crowd|time_restriction|custom)$")
    conditions: AlertConditions
    actions: Optional[AlertActions] = None
    is_active: bool = True
    priority: int = Field(default=5, ge=1, le=10)
    cooldown_seconds: int = Field(default=300, ge=0)


class AlertRuleCreate(AlertRuleBase):
    """Schema for creating an alert rule."""
    pass


class AlertRuleUpdate(BaseModel):
    """Schema for updating an alert rule."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    rule_type: Optional[str] = None
    conditions: Optional[AlertConditions] = None
    actions: Optional[AlertActions] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1, le=10)
    cooldown_seconds: Optional[int] = Field(None, ge=0)


class AlertRuleResponse(AlertRuleBase):
    """Schema for alert rule response."""
    rule_id: UUID
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AlertLogResponse(BaseModel):
    """Schema for alert log response."""
    alert_id: UUID
    rule_id: Optional[UUID]
    rule_name: Optional[str]
    rule_type: Optional[str]
    subject_id: Optional[UUID]
    subject_label: Optional[str]
    camera_id: Optional[UUID]
    camera_name: Optional[str]
    trigger_data: Dict[str, Any]
    status: str
    priority: Optional[int]
    acknowledged_by: Optional[UUID]
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    age_minutes: Optional[float]
    
    class Config:
        from_attributes = True


class AlertAcknowledgeRequest(BaseModel):
    """Schema for acknowledging an alert."""
    notes: Optional[str] = None


class AlertResolveRequest(BaseModel):
    """Schema for resolving an alert."""
    notes: Optional[str] = None


class AlertStatsResponse(BaseModel):
    """Schema for alert statistics."""
    total_alerts: int
    open_alerts: int
    acknowledged_alerts: int
    resolved_alerts: int
    false_positive_alerts: int
    alerts_by_priority: Dict[int, int]
    alerts_by_rule_type: Dict[str, int]
