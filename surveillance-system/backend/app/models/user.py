"""User model for authentication and RBAC."""

from datetime import datetime, timedelta
from uuid import uuid4
from typing import Optional, Dict, Any

from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class User(Base):
    """System user with RBAC."""
    
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="viewer")  # admin, operator, viewer, auditor
    department = Column(String(100))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255))
    password_changed_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert model to dictionary."""
        data = {
            "user_id": str(self.user_id),
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "department": self.department,
            "is_active": self.is_active,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "mfa_enabled": self.mfa_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        
        if include_sensitive:
            data["login_attempts"] = self.login_attempts
            data["locked_until"] = self.locked_until.isoformat() if self.locked_until else None
            data["password_changed_at"] = self.password_changed_at.isoformat() if self.password_changed_at else None
        
        return data
    
    def record_login(self, success: bool = True) -> None:
        """Record login attempt."""
        if success:
            self.last_login = datetime.utcnow()
            self.login_attempts = 0
            self.locked_until = None
        else:
            self.login_attempts += 1
            if self.login_attempts >= 5:
                self.locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def is_locked(self) -> bool:
        """Check if account is locked."""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission."""
        role_permissions = {
            "admin": ["*"],
            "operator": [
                "cameras:read", "cameras:write",
                "subjects:read", "subjects:write",
                "sightings:read",
                "alerts:read", "alerts:write",
                "analytics:read"
            ],
            "viewer": [
                "cameras:read",
                "subjects:read",
                "sightings:read",
                "alerts:read",
                "analytics:read"
            ],
            "auditor": [
                "audit:read",
                "reports:read"
            ]
        }
        
        permissions = role_permissions.get(self.role, [])
        return "*" in permissions or permission in permissions
