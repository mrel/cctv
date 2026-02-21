"""Alert models for rule configuration and alert logs."""

from datetime import datetime
from uuid import uuid4
from typing import Optional, Dict, Any

from sqlalchemy import Column, String, DateTime, JSON, Float, Integer, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class AlertRule(Base):
    """Alert rule configuration."""
    
    __tablename__ = "alert_rules"
    
    rule_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    rule_type = Column(String(50), nullable=False)  # blacklist, whitelist, geofence, loitering, tailgating
    conditions = Column(JSON, nullable=False)
    actions = Column(JSON)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=5)
    cooldown_seconds = Column(Integer, default=300)
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    alert_logs = relationship("AlertLog", back_populates="rule")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "rule_id": str(self.rule_id),
            "name": self.name,
            "description": self.description,
            "rule_type": self.rule_type,
            "conditions": self.conditions,
            "actions": self.actions,
            "is_active": self.is_active,
            "priority": self.priority,
            "cooldown_seconds": self.cooldown_seconds,
            "created_by": str(self.created_by) if self.created_by else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def should_trigger(self, context: Dict[str, Any]) -> bool:
        """
        Evaluate if rule should trigger based on context.
        Context contains: subject, camera, sighting, etc.
        """
        if not self.is_active:
            return False
        
        conditions = self.conditions or {}
        
        # Check subject type filter
        if "subject_types" in conditions:
            subject = context.get("subject")
            if not subject or subject.subject_type not in conditions["subject_types"]:
                return False
        
        # Check camera filter
        if "cameras" in conditions:
            camera = context.get("camera")
            if not camera or str(camera.camera_id) not in conditions["cameras"]:
                return False
        
        # Check confidence threshold
        if "min_confidence" in conditions:
            sighting = context.get("sighting")
            if not sighting or sighting.recognition_confidence < conditions["min_confidence"]:
                return False
        
        return True


class AlertLog(Base):
    """Log of triggered alerts."""
    
    __tablename__ = "alert_logs"
    
    alert_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("alert_rules.rule_id", ondelete="SET NULL"))
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.subject_id", ondelete="SET NULL"))
    camera_id = Column(UUID(as_uuid=True), ForeignKey("cameras.camera_id", ondelete="SET NULL"))
    sighting_id = Column(UUID(as_uuid=True), ForeignKey("sightings.sighting_id", ondelete="SET NULL"))
    trigger_data = Column(JSON, nullable=False)
    status = Column(String(50), default="open")  # open, acknowledged, resolved, false_positive, escalated
    priority = Column(Integer)
    acknowledged_by = Column(UUID(as_uuid=True))
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    rule = relationship("AlertRule", back_populates="alert_logs")
    subject = relationship("Subject", back_populates="alert_logs")
    camera = relationship("Camera", back_populates="alert_logs")
    sighting = relationship("Sighting", back_populates="alert_logs")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "alert_id": str(self.alert_id),
            "rule_id": str(self.rule_id) if self.rule_id else None,
            "subject_id": str(self.subject_id) if self.subject_id else None,
            "camera_id": str(self.camera_id) if self.camera_id else None,
            "sighting_id": str(self.sighting_id) if self.sighting_id else None,
            "trigger_data": self.trigger_data,
            "status": self.status,
            "priority": self.priority,
            "acknowledged_by": str(self.acknowledged_by) if self.acknowledged_by else None,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def acknowledge(self, user_id: str) -> None:
        """Acknowledge the alert."""
        self.status = "acknowledged"
        self.acknowledged_by = user_id
        self.acknowledged_at = datetime.utcnow()
    
    def resolve(self) -> None:
        """Resolve the alert."""
        self.status = "resolved"
        self.resolved_at = datetime.utcnow()
