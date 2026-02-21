"""Audit log model for GDPR compliance and security monitoring."""

from datetime import datetime
from uuid import uuid4
from typing import Optional, Dict, Any

from sqlalchemy import Column, String, DateTime, JSON, Text, INET
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class AuditLog(Base):
    """Immutable audit trail for compliance."""
    
    __tablename__ = "audit_logs"
    
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True))
    user_role = Column(String(50))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(UUID(as_uuid=True))
    details = Column(JSON)
    ip_address = Column(INET)
    user_agent = Column(Text)
    session_id = Column(String(255))
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
    compliance_context = Column(JSON)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "log_id": str(self.log_id),
            "user_id": str(self.user_id) if self.user_id else None,
            "user_role": self.user_role,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": str(self.resource_id) if self.resource_id else None,
            "details": self.details,
            "ip_address": str(self.ip_address) if self.ip_address else None,
            "user_agent": self.user_agent,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "compliance_context": self.compliance_context
        }
    
    @classmethod
    def create_log(
        cls,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None,
        details: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        compliance_context: Optional[Dict] = None
    ) -> "AuditLog":
        """Create a new audit log entry."""
        return cls(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            user_role=user_role,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            compliance_context=compliance_context
        )
