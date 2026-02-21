"""Subject model for person identity management."""

from datetime import datetime
from uuid import uuid4
from typing import Optional, Dict, Any, List

from sqlalchemy import Column, String, DateTime, JSON, Float, Integer
from sqlalchemy.dialects.postgresql import UUID, VECTOR
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.config import settings


class Subject(Base):
    """Person identity with facial recognition embeddings."""
    
    __tablename__ = "subjects"
    
    subject_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    label = Column(String(255))  # "John Doe" or "Unknown-4521"
    subject_type = Column(String(50), default="unknown")  # employee, visitor, banned, vip
    status = Column(String(50), default="active")
    primary_embedding = Column(VECTOR(settings.EMBEDDING_DIMENSION))
    enrollment_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_seen = Column(DateTime(timezone=True))
    metadata = Column(JSON)  # age, gender, ethnicity, etc.
    consent_status = Column(String(50), default="pending")  # GDPR compliance
    retention_until = Column(DateTime(timezone=True))
    
    # Relationships
    images = relationship("Image", back_populates="subject", cascade="all, delete-orphan")
    sightings = relationship("Sighting", back_populates="subject")
    alert_logs = relationship("AlertLog", back_populates="subject")
    
    def to_dict(self, include_embedding: bool = False) -> Dict[str, Any]:
        """Convert model to dictionary."""
        data = {
            "subject_id": str(self.subject_id),
            "label": self.label,
            "subject_type": self.subject_type,
            "status": self.status,
            "enrollment_date": self.enrollment_date.isoformat() if self.enrollment_date else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "metadata": self.metadata,
            "consent_status": self.consent_status,
            "retention_until": self.retention_until.isoformat() if self.retention_until else None,
            "image_count": len(self.images) if self.images else 0,
            "sighting_count": len(self.sightings) if self.sightings else 0
        }
        
        if include_embedding and self.primary_embedding:
            data["primary_embedding"] = self.primary_embedding.tolist()
        
        return data
    
    def update_last_seen(self) -> None:
        """Update last seen timestamp."""
        self.last_seen = datetime.utcnow()
    
    @property
    def best_image(self) -> Optional["Image"]:
        """Get the best quality image for this subject."""
        if not self.images:
            return None
        
        # Sort by quality score and return best
        sorted_images = sorted(
            [img for img in self.images if img.quality_score is not None],
            key=lambda x: x.quality_score or 0,
            reverse=True
        )
        
        return sorted_images[0] if sorted_images else self.images[0]
